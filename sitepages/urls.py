from django.urls import path

from . import views

app_name = "sitepages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("contact/thank-you/", views.contact_thank_you, name="contact_thank_you"),
    path("track/", views.track_shipment, name="track"),
    path("quote/", views.request_quote, name="quote"),
    path("quote/thank-you/", views.quote_success, name="quote_success"),
]
