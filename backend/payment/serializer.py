from rest_framework import serializers


class WebhookSerializer(serializers.Serializer):
    payment_id = serializers.UUIDField()
    result = serializers.ChoiceField(choices=["pending", "success", "failed"])
