from rest_framework import serializers

from .models import Document, Shipment, StatusUpdate


class StatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusUpdate
        fields = ["id", "status", "note", "created_at"]
        read_only_fields = fields


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "doc_type", "file", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class ShipmentSerializer(serializers.ModelSerializer):
    status_updates = StatusUpdateSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id", "reference", "branch", "mode", "origin", "destination",
            "bill_of_lading", "airway_bill", "status", "eta",
            "created_at", "updated_at", "status_updates", "documents",
        ]
        read_only_fields = ["id", "reference", "status", "created_at", "updated_at"]


class StatusUpdateCreateSerializer(serializers.ModelSerializer):
    """Used by staff to push a new status — triggers the notification signal."""

    class Meta:
        model = StatusUpdate
        fields = ["status", "note"]

    def create(self, validated_data):
        shipment = self.context["shipment"]
        staff = self.context["request"].user.staff_profile
        return StatusUpdate.objects.create(shipment=shipment, created_by=staff, **validated_data)
