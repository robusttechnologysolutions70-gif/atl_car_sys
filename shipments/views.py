from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Shipment
from .serializers import ShipmentSerializer, StatusUpdateCreateSerializer


class ShipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Clients see only their own shipments.
    Staff see all shipments in their branch.
    Lookup also works by `reference` (e.g. ACS-1A2B3C4D) for the public tracking box.
    """

    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "reference"

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "client_profile"):
            return Shipment.objects.filter(client=user.client_profile)
        if hasattr(user, "staff_profile"):
            return Shipment.objects.filter(branch=user.staff_profile.branch)
        return Shipment.objects.none()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def add_status_update(self, request, reference=None):
        """Staff-only: push a new status, which fans out client notifications."""
        shipment = self.get_object()
        if not hasattr(request.user, "staff_profile"):
            return Response({"detail": "Staff only."}, status=403)
        serializer = StatusUpdateCreateSerializer(
            data=request.data, context={"request": request, "shipment": shipment}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ShipmentSerializer(shipment).data, status=201)
