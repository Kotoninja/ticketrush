from django.urls import path
from .views import BookingRetrieveView

urlpatterns = [
    path("<int:user>/<int:seat_session>/", BookingRetrieveView.as_view(), name="booking-detail")
]
