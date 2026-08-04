from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(
        "ws/booking/<int:venue_id>/<int:hall_id>/", consumers.BookingConsumer.as_asgi()
    ),
]
