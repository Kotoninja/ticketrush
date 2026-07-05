from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Venue


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = "__all__"

    def validate(self, attrs):
        instance = self.Meta.model(**attrs)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e)

        return super().validate(attrs)
