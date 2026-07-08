from rest_framework import serializers

from .models import EventSession, SeatSession


class SeatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatSession
        exclude = ["created_at", "updated_at"]


class EventSessionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at", "updated_at"]

    seats = SeatSessionSerializer(many=True)


class EventSessionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at", "updated_at"]
