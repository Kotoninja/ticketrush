from rest_framework import serializers
from session.serializers import SeatSessionWithFullDetail

from .models import Booking


class BookingReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        exclude = ["user"]

    seat_session = SeatSessionWithFullDetail()


class BookingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        exclude = ["created_at", "updated_at", "status", "draft_expire_time", "user"]
