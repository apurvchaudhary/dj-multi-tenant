from channels.generic.websocket import AsyncWebsocketConsumer
import json


class UpdateConsumer(AsyncWebsocketConsumer):
    group_name = "updates"

    async def connect(self):
        # Join the WebSocket group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_update(self, event):
        message = event["message"]
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({"update": message}))
