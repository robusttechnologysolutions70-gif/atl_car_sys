from rest_framework.routers import DefaultRouter

from .views import QuoteRequestViewSet

router = DefaultRouter()
router.register("quotes", QuoteRequestViewSet, basename="quote")

urlpatterns = router.urls
