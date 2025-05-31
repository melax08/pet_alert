import asyncio
import logging
from collections import deque
from collections.abc import Collection
from typing import Self

from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError, TelegramRetryAfter
from aiogram.types import FSInputFile, InputFile
from django.conf import settings

from server.apps.ads.models import Advertisement

from .constants import ADV_ATTRIBUTE_TEMPLATE_MAP
from .utils import ThumbnailImage


class TelegramNotificationsService:
    simultaneous_notifications_per_second: int = 25

    def __init__(self, bot_token: str) -> None:
        self._bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self._sending_queue: deque[int] = deque()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Exit async context and close the bot session."""
        await self._bot.session.close()

    async def bulk_send_telegram_message(
        self, telegram_ids: Collection[int], message: str, media_file_path: str | None
    ) -> None:
        """
        Send message from telegram bot to users with specified telegram ids.
        Respect telegram bot sending limits:
        https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this
        """
        self._sending_queue.extend(telegram_ids)

        file_id = None
        if media_file_path is not None:
            file = FSInputFile(path=f"{settings.MEDIA_ROOT}/{media_file_path}")
            file_id = await self._preupload_media_file(message, file)

            if not file_id:
                logging.info("File id was not received, sending is cancelled")
                return

        while self._sending_queue:
            count = min(len(self._sending_queue), self.simultaneous_notifications_per_second)
            await asyncio.gather(
                *[
                    self.send_telegram_message(self._sending_queue.popleft(), message, file_id)
                    for _ in range(count)
                ]
            )
            await asyncio.sleep(1)

    async def send_telegram_message(
        self, telegram_id: int, message: str, media_file: InputFile | str | None
    ) -> None:
        """Send a message to the user in Telegram."""
        try:
            if media_file:
                await self._send_photo(telegram_id, message, media_file)
            else:
                await self._send_message(telegram_id, message)
        except TelegramRetryAfter:
            logging.warning(
                f'Ratelimit while sending notification to the user with tg id: "{telegram_id}"'
            )
            self._sending_queue.append(telegram_id)
        except AiogramError as e:
            logging.warning(
                f"An error occurred while trying to send a notification to the user: "
                f'"{telegram_id}" - {str(e)}'
            )

    async def _preupload_media_file(self, message: str, media_file: InputFile) -> str | None:
        """
        Try to send photo to the telegram users in queue, if success - return the photo file_id.
        file_id is needed to reuse this photo the next time you send it, to avoid re-uploading
        the same photo to Telegram servers.
        """
        while self._sending_queue:
            file_id = await self._send_photo(
                telegram_id=self._sending_queue.popleft(), message=message, photo=media_file
            )
            if file_id is not None:
                return file_id

    async def _send_photo(self, telegram_id: int, message: str, photo: InputFile | str) -> str:
        """
        Send the message with photo to the Telegram user.
        Return photo file_id to send this photo again if needed.
        """
        message = await self._bot.send_photo(chat_id=telegram_id, caption=message, photo=photo)
        return message.photo[-1].file_id

    async def _send_message(self, telegram_id: int, message: str) -> None:
        """Send the common message to the telegram user."""
        await self._bot.send_message(chat_id=telegram_id, text=message)


class AdvertisementTelegramNotificationService:
    def send_advertisement_to_telegram_users(
        self, telegram_ids: list[int], advertisement: Advertisement
    ) -> None:
        message, image_path = self._serialize_advertisement(advertisement)

        with ThumbnailImage(image_path) as thumbnail:
            asyncio.run(
                self._send_telegram_message_to_many_users(
                    telegram_ids,
                    message,
                    thumbnail.thumbnail.name if thumbnail is not None else None,
                )
            )

    @staticmethod
    async def _send_telegram_message_to_many_users(
        telegram_ids: list[int], message: str, image_path: str | None
    ) -> None:
        async with TelegramNotificationsService(settings.TELEGRAM_TOKEN) as service:
            await service.bulk_send_telegram_message(
                telegram_ids=telegram_ids,
                message=message,
                media_file_path=image_path,
            )

    def _serialize_advertisement(self, adv_instance: Advertisement) -> tuple[str, str | None]:
        """Serialize lost or found advertisement to the tuple with information message about
        the advertisement and image path."""
        try:
            image_path = adv_instance.image.path
        except ValueError:
            image_path = None

        message = self._generate_info_message_about_advertisement(adv_instance)

        return message, image_path

    @staticmethod
    def _generate_info_message_about_advertisement(adv_instance: Advertisement) -> str:
        message = [
            "❗ Создано новое объявление!",
            f"<b>Автор</b>: {adv_instance.author.first_name} ({adv_instance.author.email})",
        ]

        for attribute, template in ADV_ATTRIBUTE_TEMPLATE_MAP.items():
            adv_attribute_value = getattr(adv_instance, attribute, None)
            if adv_attribute_value:
                message.append(template.format(adv_attribute_value))

        return "\n".join(message)
