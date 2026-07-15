from django.urls import path
from rest_framework import routers

from .views import EventSessionAPI, SeatSessionAPI, index

router = routers.SimpleRouter()
router.register("", EventSessionAPI)

urlpatterns = [
    path("index/", index),
    path(
        "seat/<int:event_session_pk>/<int:seat_session_pk>",
        SeatSessionAPI.as_view(),
        name="seat-session-detail",
    ),
] + router.urls
