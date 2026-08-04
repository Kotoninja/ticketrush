import json

from channels.generic.websocket import AsyncWebsocketConsumer
from drf_spectacular_websocket.decorators import extend_ws_schema
from rest_framework import serializers


class MessageResponseSerializer(serializers.Serializer):
    seat_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=["free", "draft", "busy"])


class BookingConsumer(AsyncWebsocketConsumer):
    @extend_ws_schema(responses={200: MessageResponseSerializer})
    async def connect(self):
        self.hall_id = self.scope["url_route"]["kwargs"]["hall_id"]
        self.room_group_name = f"booking_{self.hall_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def booking_update(self, event):
        seat_id = event["seat_id"]
        status = event["status"]

        await self.send(text_data=json.dumps({"seat_id": seat_id, "status": status}))
