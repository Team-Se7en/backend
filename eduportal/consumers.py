from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id
        if not self.user_id:
            await self.close()
            return
        self.group_name = f"notification_{self.user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        print("send_notification:\t\tDebug:\t\tStarting sending of ws message.")
        
        try:
            message = event["message"]
            print("send_notification:\t\tDebug:\t\tRetrieved event message.")
            message_data = json.dumps(message)
            print("send_notification:\t\tDebug:\t\tRetrieved message data json.")
            await self.send(text_data=message_data)
            print(f"sent notif: {message_data}\n to user {self.user_id}")
        except Exception as e:
            print("send_notification:\t\tDebug:\t\tException occured:")
            print(f"send_notification:\t\tDebug:\t\t{e}")
