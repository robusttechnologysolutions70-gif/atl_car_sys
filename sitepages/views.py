from django.db.models import Q
from django.shortcuts import redirect, render

from shipments.models import Shipment

from .forms import ContactMessageForm, QuoteRequestForm


def home(request):
    return render(request, "sitepages/home.html")


def about(request):
    return render(request, "sitepages/about.html")


def services(request):
    return render(request, "sitepages/services.html")


def contact(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sitepages:contact_thank_you")
    else:
        form = ContactMessageForm()
    return render(request, "sitepages/contact.html", {"form": form})


def contact_thank_you(request):
    return render(request, "sitepages/contact_thank_you.html")


def track_shipment(request):
    query = request.GET.get("ref", "").strip()
    shipment = None
    searched = bool(query)
    if searched:
        shipment = (
            Shipment.objects.filter(
                Q(reference__iexact=query) | Q(bill_of_lading__iexact=query) | Q(airway_bill__iexact=query)
            )
            .prefetch_related("status_updates")
            .first()
        )
    return render(
        request,
        "sitepages/track.html",
        {"shipment": shipment, "searched": searched, "query": query},
    )


def request_quote(request):
    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sitepages:quote_success")
    else:
        form = QuoteRequestForm()
    return render(request, "sitepages/quote.html", {"form": form})


def quote_success(request):
    return render(request, "sitepages/quote_success.html")
