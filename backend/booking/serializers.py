from rest_framework import serializers
from session.serializers import SeatSessionWithFullDetail

from .models import Booking


class BookingReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

    seat_session = SeatSessionWithFullDetail()


class BookingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        exclude = ["created_at", "updated_at", "status"]
