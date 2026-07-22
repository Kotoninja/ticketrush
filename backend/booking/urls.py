from django.urls import path

from .views import (
    BookingCreateView,
    BookingDeleteView,
    BookingListView,
    BookingRetrieveView,
    BookingPayView,
)

urlpatterns = [
    path("<int:pk>/", BookingDeleteView.as_view(), name="booking-detail"),
    path(
        "session/<int:seat_session_pk>/",
        BookingRetrieveView.as_view(),
        name="booking-detail",
    ),
    path("", BookingCreateView.as_view(), name="booking-list"),
    path("list/", BookingListView.as_view(), name="booking-list"),
    path("<int:pk>/pay/", BookingPayView.as_view(), name="booking-list"),
]
