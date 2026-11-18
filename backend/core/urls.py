
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    GuideViewSet,
    AttractionViewSet,
    BookingViewSet,
    ItineraryView,
)

router = DefaultRouter()
router.register("guides", GuideViewSet)
router.register("attractions", AttractionViewSet)
router.register("bookings", BookingViewSet)

urlpatterns = [
    path("itinerary/", ItineraryView.as_view(), name="itinerary"),
] + router.urls
