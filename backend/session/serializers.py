from event.serializers import EventBaseSerializer, EventSerializerWithoutDescription
from hall.serializer import HallBaseSerializer
from rest_framework import serializers
from seat.serializer import SeatSerializer

from .models import EventSession, SeatSession


class SeatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatSession
        exclude = ["created_at", "updated_at", "event_session"]


class EventSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at", "updated_at"]


class EventSessionEventAndHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at", "updated_at", "hall"]

    event = EventBaseSerializer()


class EventSessionSerializerWithFullDetail(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at", "updated_at"]
        depth = 2


class SeatSessionWithFullDetail(serializers.ModelSerializer):
    class Meta:
        model = SeatSession
        exclude = ["created_at", "updated_at"]

    event_session = EventSessionEventAndHallSerializer()
    seat = SeatSerializer()


class EventSessionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at", "updated_at"]

    seats_count = serializers.SerializerMethodField()
    event = EventSerializerWithoutDescription()
    hall = HallBaseSerializer()

    def get_seats_count(self, obj) -> int:
        return obj.seats.count()


class EventSessionRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at", "updated_at"]

    seats = SeatSessionSerializer(many=True)
    event = EventSerializerWithoutDescription()
    hall = HallBaseSerializer()


class EventSessionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at", "updated_at"]
