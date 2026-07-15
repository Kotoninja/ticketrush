from rest_framework import serializers
from .models import Booking
from session.serializers import SeatSessionWithFullDetail


class BookingReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

    seat_session = SeatSessionWithFullDetail()
