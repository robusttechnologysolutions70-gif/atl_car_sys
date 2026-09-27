from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from accounts.models import ClientProfile, StaffProfile
from quotes.models import QuoteRequest
from shipments.models import Document, Shipment, StatusUpdate

from .forms import ClientProfileForm, ShipmentCreateForm, StaffProfileCreateForm


def _is_staff_user(user):
    return hasattr(user, "staff_profile")


def _is_admin_staff(user):
    return _is_staff_user(user) and user.staff_profile.role == StaffProfile.Role.ADMIN


class RoleAwareShipmentMixin(LoginRequiredMixin):
    """Clients see only their own shipments; staff see their branch's."""

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "client_profile"):
            return Shipment.objects.filter(client=user.client_profile)
        if hasattr(user, "staff_profile"):
            return Shipment.objects.filter(branch=user.staff_profile.branch)
        return Shipment.objects.none()


class ShipmentListView(RoleAwareShipmentMixin, ListView):
    model = Shipment
    template_name = "portal/shipment_list.html"
    context_object_name = "shipments"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_staff_user"] = _is_staff_user(self.request.user)
        return context


class ShipmentDetailView(RoleAwareShipmentMixin, DetailView):
    model = Shipment
    template_name = "portal/shipment_detail.html"
    context_object_name = "shipment"
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        return get_object_or_404(queryset, reference=self.kwargs["reference"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_staff_user"] = _is_staff_user(self.request.user)
        context["status_updates"] = self.object.status_updates.all().order_by("-created_at")
        context["documents"] = self.object.documents.all()
        return context


@login_required
def dashboard(request):
    """Landing page after login — staff go to the branch dashboard, clients to their shipments."""
    if _is_staff_user(request.user):
        return redirect("portal:staff_dashboard")
    return redirect("portal:shipment_list")


@login_required
def staff_dashboard(request):
    if not _is_staff_user(request.user):
        return redirect("portal:shipment_list")

    branch = request.user.staff_profile.branch
    shipments = Shipment.objects.filter(branch=branch)
    status_counts = shipments.values("status").annotate(count=Count("id")).order_by()
    quote_requests = QuoteRequest.objects.filter(
        preferred_branch=branch, status=QuoteRequest.Status.NEW
    ).order_by("-created_at")[:10]
    recent_shipments = shipments.order_by("-created_at")[:10]

    return render(
        request,
        "portal/staff_dashboard.html",
        {
            "total_shipments": shipments.count(),
            "status_counts": status_counts,
            "quote_requests": quote_requests,
            "recent_shipments": recent_shipments,
            "is_admin_staff": _is_admin_staff(request.user),
        },
    )


@login_required
def add_status_update(request, reference):
    """Staff-only form post: creates a StatusUpdate, which fires the notification signal."""
    if not _is_staff_user(request.user) or request.method != "POST":
        raise Http404
    shipment = get_object_or_404(Shipment, reference=reference, branch=request.user.staff_profile.branch)
    status = request.POST.get("status")
    note = request.POST.get("note", "")
    valid_statuses = dict(Shipment._meta.get_field("status").choices)
    if status in valid_statuses:
        StatusUpdate.objects.create(
            shipment=shipment, status=status, note=note, created_by=request.user.staff_profile
        )
        messages.success(request, f"{shipment.reference} marked as {valid_statuses[status]}.")
    return redirect("portal:shipment_detail", reference=reference)


@login_required
def upload_document(request, reference):
    """Staff-only: attach a document (BOL, AWB, customs, invoice) to a shipment."""
    if not _is_staff_user(request.user) or request.method != "POST":
        raise Http404
    shipment = get_object_or_404(Shipment, reference=reference, branch=request.user.staff_profile.branch)
    doc_type = request.POST.get("doc_type")
    uploaded_file = request.FILES.get("file")
    valid_types = dict(Document._meta.get_field("doc_type").choices)
    if doc_type in valid_types and uploaded_file:
        Document.objects.create(
            shipment=shipment, doc_type=doc_type, file=uploaded_file, uploaded_by=request.user
        )
        messages.success(request, f"{valid_types[doc_type]} uploaded to {shipment.reference}.")
    else:
        messages.error(request, "Choose a document type and a file to upload.")
    return redirect("portal:shipment_detail", reference=reference)


@login_required
def convert_quote(request, quote_id):
    """
    Staff-only: turn a QuoteRequest into a real Shipment.
    Creates (or reuses) a client account keyed on phone number, since that's
    the one field every quote request has.
    """
    if not _is_staff_user(request.user) or request.method != "POST":
        raise Http404
    quote = get_object_or_404(
        QuoteRequest, id=quote_id, preferred_branch=request.user.staff_profile.branch
    )

    user, user_created = User.objects.get_or_create(
        username=quote.phone_number, defaults={"email": quote.email}
    )
    if user_created:
        user.set_unusable_password()
        user.save()

    client, _ = ClientProfile.objects.get_or_create(
        user=user,
        defaults={"company_name": quote.company_name, "phone_number": quote.phone_number},
    )

    shipment = Shipment.objects.create(
        client=client,
        branch=quote.preferred_branch,
        mode=quote.mode,
        origin=quote.origin,
        destination=quote.destination,
    )
    StatusUpdate.objects.create(
        shipment=shipment,
        status="booked",
        note="Converted from quote request",
        created_by=request.user.staff_profile,
    )
    quote.status = QuoteRequest.Status.CONVERTED
    quote.save(update_fields=["status"])

    messages.success(request, f"Quote from {quote.full_name} converted to shipment {shipment.reference}.")
    return redirect("portal:shipment_detail", reference=shipment.reference)


# --- Staff-facing admin: clients, shipments, staff accounts ---
# Replaces the need to use Django's raw /admin/ for day-to-day operations.

@login_required
def client_list(request):
    if not _is_staff_user(request.user):
        return redirect("portal:shipment_list")
    clients = ClientProfile.objects.select_related("user").order_by("company_name")
    return render(request, "portal/client_list.html", {"clients": clients})


@login_required
def client_create(request):
    if not _is_staff_user(request.user):
        return redirect("portal:shipment_list")

    if request.method == "POST":
        form = ClientProfileForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if User.objects.filter(username=username).exists():
                form.add_error("username", "That username is already taken.")
            else:
                user = User.objects.create_user(username=username)
                user.set_unusable_password()
                user.save()
                client = form.save(commit=False)
                client.user = user
                client.save()
                messages.success(request, f"Client account created for {client.company_name or username}.")
                return redirect("portal:client_list")
    else:
        form = ClientProfileForm()
    return render(request, "portal/client_form.html", {"form": form})


@login_required
def shipment_create(request):
    """Staff-only: create a shipment directly, not only via quote conversion."""
    if not _is_staff_user(request.user):
        return redirect("portal:shipment_list")

    if request.method == "POST":
        form = ShipmentCreateForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.branch = request.user.staff_profile.branch
            shipment.save()
            StatusUpdate.objects.create(
                shipment=shipment,
                status="booked",
                note="Created directly by staff",
                created_by=request.user.staff_profile,
            )
            messages.success(request, f"Shipment {shipment.reference} created.")
            return redirect("portal:shipment_detail", reference=shipment.reference)
    else:
        form = ShipmentCreateForm()
    return render(request, "portal/shipment_form.html", {"form": form})


@login_required
def staff_list(request):
    """Admin-role staff only: see and manage other staff accounts."""
    if not _is_admin_staff(request.user):
        return redirect("portal:staff_dashboard")
    staff = StaffProfile.objects.select_related("user").order_by("branch", "user__username")
    return render(request, "portal/staff_list.html", {"staff": staff})


@login_required
def staff_create(request):
    """Admin-role staff only: create another staff account with a branch and role."""
    if not _is_admin_staff(request.user):
        return redirect("portal:staff_dashboard")

    if request.method == "POST":
        form = StaffProfileCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if User.objects.filter(username=username).exists():
                form.add_error("username", "That username is already taken.")
            else:
                try:
                    validate_password(form.cleaned_data["password"])
                except ValidationError as exc:
                    for err in exc.messages:
                        form.add_error("password", err)
            if not form.errors:
                user = User.objects.create_user(
                    username=username,
                    email=form.cleaned_data.get("email", ""),
                    password=form.cleaned_data["password"],
                )
                StaffProfile.objects.create(
                    user=user, branch=form.cleaned_data["branch"], role=form.cleaned_data["role"]
                )
                messages.success(request, f"Staff account created for {username}.")
                return redirect("portal:staff_list")
    else:
        form = StaffProfileCreateForm()
    return render(request, "portal/staff_form.html", {"form": form})
