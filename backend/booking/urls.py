from django.urls import path

from .views import BookingCreateView, BookingDeleteView, BookingRetrieveView

urlpatterns = [
    path(
        "<int:user_pk>/<int:seat_session_pk>/",
        BookingRetrieveView.as_view(),
        name="booking-detail",
    ),
    path("", BookingCreateView.as_view(), name="booking-list"),
    path("<int:pk>/", BookingDeleteView.as_view(), name="booking-detail"),
]
