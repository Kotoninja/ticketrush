from rest_framework import serializers

from .models import EventSession


class EventSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        exclude = ["created_at","updated_at"]