from rest_framework import serializers

from .models import QuoteRequest


class QuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = [
            "id", "full_name", "company_name", "phone_number", "email",
            "mode", "origin", "destination", "cargo_description",
            "weight_kg", "volume_cbm", "preferred_branch", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]
