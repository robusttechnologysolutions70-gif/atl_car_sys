from django import forms

from quotes.models import QuoteRequest

from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone_number", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }


class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = [
            "full_name", "company_name", "phone_number", "email",
            "mode", "origin", "destination", "cargo_description",
            "weight_kg", "volume_cbm", "preferred_branch",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+256 7xx xxx xxx"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "mode": forms.Select(attrs={"class": "form-select"}),
            "origin": forms.TextInput(attrs={"class": "form-control"}),
            "destination": forms.TextInput(attrs={"class": "form-control"}),
            "cargo_description": forms.TextInput(attrs={"class": "form-control"}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "volume_cbm": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "preferred_branch": forms.Select(attrs={"class": "form-select"}),
        }
