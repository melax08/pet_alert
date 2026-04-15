import json
from typing import Any

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from server.apps.user_profile.messenger.choices import DialogConsumerActionTypeChoices
from server.apps.user_profile.messenger.services import MessengerService


class DialogConsumer(AsyncWebsocketConsumer):
    """Async chat websocket dialog consumer."""

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        dialog_id = self.scope["url_route"]["kwargs"]["dialog_id"]

        self.service = MessengerService(user=self.user)

        self.dialog = await database_sync_to_async(self.service.get_dialog)(dialog_id)
        if not self.dialog:
            await self.close()
            return

        self.room_group_name = f"dialog_{dialog_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data: str) -> None:
        text_data_json = json.loads(text_data)

        match text_data_json.get("type"):
            case DialogConsumerActionTypeChoices.READ_MESSAGES:
                await database_sync_to_async(self.service.mark_dialog_messages_as_viewed)(
                    self.dialog
                )
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "messages_read",
                        "reader_id": self.user.id,
                    },
                )
            case DialogConsumerActionTypeChoices.SEND_MESSAGE:
                message = text_data_json.get("message")
                if not message:
                    return

                db_message = await database_sync_to_async(self.service.send_message)(
                    dialog=self.dialog, message_content=message
                )

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_message",
                        "message": message,
                        "sender_id": self.user.id,
                        "created_at": str(db_message.pub_date),
                    },
                )

    async def send_message(self, event: dict[str, Any]) -> None:
        await self.send(text_data=json.dumps(event))

    async def messages_read(self, event: dict[str, Any]) -> None:
        await self.send(text_data=json.dumps(event))
