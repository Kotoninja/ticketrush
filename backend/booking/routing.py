from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(
        "ws/booking/<int:hall_id>/", consumers.BookingConsumer.as_asgi()
    ),
]
