from rest_framework import mixins, permissions, viewsets

from .models import QuoteRequest
from .serializers import QuoteRequestSerializer


class QuoteRequestViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    POST is open to the public (the website's quote form).
    GET (list) is staff-only, filtered to their branch.
    """

    serializer_class = QuoteRequestSerializer
    queryset = QuoteRequest.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "staff_profile"):
            return QuoteRequest.objects.filter(preferred_branch=user.staff_profile.branch)
        return QuoteRequest.objects.none()
