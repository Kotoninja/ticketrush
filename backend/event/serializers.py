from rest_framework import serializers

from .models import Event


class EventBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "duration", "age_available", "category"]


class EventSerializer(EventBaseSerializer):
    class Meta(EventBaseSerializer.Meta):
        fields = EventBaseSerializer.Meta.fields + ["description", "small_description"]


class EventSerializerWithoutDescription(EventBaseSerializer): ...
