import json

from channels.generic.websocket import AsyncWebsocketConsumer


class BookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.venue_id = self.scope["url_route"]["kwargs"]["venue_id"]
        self.hall_id= self.scope["url_route"]["kwargs"]["hall_id"]
        self.room_group_name = f"booking_{self.venue_id}_{self.hall_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def booking_update(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))