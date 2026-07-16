from django.urls import path
from .views import BookingRetrieveView, BookingCreateView

urlpatterns = [
    path(
        "<int:user_pk>/<int:seat_session_pk>/",
        BookingRetrieveView.as_view(),
        name="booking-detail",
    ),
    path("", BookingCreateView.as_view(), name="booking-list"),
]
