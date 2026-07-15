from event.serializers import EventSerializerWithoutDescription
from hall.serializer import HallBaseSerializer
from rest_framework import serializers

from .models import EventSession, SeatSession


class SeatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatSession
        exclude = ["created_at", "updated_at", "event_session"]


class EventSessionSerializerWithFullDetail(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at", "updated_at"]
        depth = 2


class SeatSessionWithFullDetail(serializers.ModelSerializer):
    class Meta:
        model = SeatSession
        exclude = ["created_at", "updated_at"]
        depth = 1

    event_session = EventSessionSerializerWithFullDetail()


class EventSessionReadSerializer(serializers.ModelSerializer):
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
