from rest_framework import serializers

from .models import Hall


class HallBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = ["id", "name", "number"]


class HallSerializer(HallBaseSerializer):
    class Meta(HallBaseSerializer.Meta):
        fields = HallBaseSerializer.Meta.fields + ["venue"]
