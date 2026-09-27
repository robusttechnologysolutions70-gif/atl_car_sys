from django import forms

from accounts.models import Branch, ClientProfile, StaffProfile
from shipments.models import Shipment


class ClientProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        help_text="Login username for this client (e.g. their phone number).",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = ClientProfile
        fields = ["company_name", "phone_number", "sms_opt_in", "whatsapp_opt_in"]
        widgets = {
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+256 7xx xxx xxx"}),
            "sms_opt_in": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "whatsapp_opt_in": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ShipmentCreateForm(forms.ModelForm):
    """Branch is set server-side from the logged-in staff member, not from this form."""

    class Meta:
        model = Shipment
        fields = ["client", "mode", "origin", "destination", "bill_of_lading", "airway_bill", "eta"]
        widgets = {
            "client": forms.Select(attrs={"class": "form-select"}),
            "mode": forms.Select(attrs={"class": "form-select"}),
            "origin": forms.TextInput(attrs={"class": "form-control"}),
            "destination": forms.TextInput(attrs={"class": "form-control"}),
            "bill_of_lading": forms.TextInput(attrs={"class": "form-control"}),
            "airway_bill": forms.TextInput(attrs={"class": "form-control"}),
            "eta": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = ClientProfile.objects.order_by("company_name")
        self.fields["bill_of_lading"].required = False
        self.fields["airway_bill"].required = False
        self.fields["eta"].required = False


class StaffProfileCreateForm(forms.Form):
    """Admin-role staff only: creates a User + StaffProfile together."""

    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Temporary password — share it with them to change on first login.",
    )
    branch = forms.ChoiceField(choices=Branch.choices, widget=forms.Select(attrs={"class": "form-select"}))
    role = forms.ChoiceField(choices=StaffProfile.Role.choices, widget=forms.Select(attrs={"class": "form-select"}))
