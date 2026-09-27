from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),

    # Shipments — "new" must be registered before the <reference> catch-all
    path("shipments/new/", views.shipment_create, name="shipment_create"),
    path("shipments/", views.ShipmentListView.as_view(), name="shipment_list"),
    path("shipments/<str:reference>/", views.ShipmentDetailView.as_view(), name="shipment_detail"),
    path("shipments/<str:reference>/status/", views.add_status_update, name="add_status_update"),
    path("shipments/<str:reference>/documents/", views.upload_document, name="upload_document"),

    # Quotes
    path("quotes/<uuid:quote_id>/convert/", views.convert_quote, name="convert_quote"),

    # Clients (staff-managed)
    path("clients/", views.client_list, name="client_list"),
    path("clients/new/", views.client_create, name="client_create"),

    # Staff accounts (admin-role only)
    path("staff-accounts/", views.staff_list, name="staff_list"),
    path("staff-accounts/new/", views.staff_create, name="staff_create"),
]
