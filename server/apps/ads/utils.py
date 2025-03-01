import asyncio
import logging

from sorl.thumbnail import delete, get_thumbnail
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from .constants import (
    ADV_ATTRIBUTE_TEMPLATE_MAP,
    THUMBNAIL_CROP,
    THUMBNAIL_GEOMETRY,
    THUMBNAIL_QUALITY,
)


def serialize_advertisement(adv_instance) -> dict:
    """Serialize Lost and Found advertisements to the dictionary with image path
    and information message about advertisement."""
    try:
        image_path = adv_instance.image.path
    except ValueError:
        image_path = None

    message = generate_info_message_about_advertisement(adv_instance)

    return {"image_path": image_path, "message": message}


def generate_info_message_about_advertisement(adv_instance) -> str:
    message = [
        "❗ Создано новое объявление!",
        f"<b>Автор</b>: {adv_instance.author.first_name} ({adv_instance.author.email})",
    ]

    for attribute, template in ADV_ATTRIBUTE_TEMPLATE_MAP.items():
        adv_attribute_value = getattr(adv_instance, attribute, None)
        if adv_attribute_value:
            message.append(template.format(adv_attribute_value))

    return "\n".join(message)


class SubstituteImage:
    """Creates a thumbnail of image in advertisement data and removes it after use."""

    def __init__(self, adv_data: dict):
        self.adv_data = adv_data

    def __enter__(self):
        image_path = self.adv_data.get("image_path")
        if image_path:
            self.thumbnail = get_thumbnail(
                image_path,
                THUMBNAIL_GEOMETRY,
                crop=THUMBNAIL_CROP,
                quality=THUMBNAIL_QUALITY,
            )
            self.adv_data["image_path"] = self.thumbnail

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "thumbnail"):
            delete(self.thumbnail)


async def send_telegram_message(bot_instance: Bot, telegram_id: int, adv_data: dict):
    """Sends the telegram message to the specified telegram user."""
    image_path = adv_data.get("image_path")
    message = adv_data.get("message")
    try:
        if image_path:
            await bot_instance.send_photo(
                telegram_id, image_path, message, parse_mode=ParseMode.HTML
            )
        else:
            await bot_instance.send_message(telegram_id, message, parse_mode=ParseMode.HTML)
    except TelegramError as error:
        logging.error(
            f"A telegram error occurred while sending a message about the "
            f"new advertisement to {telegram_id}: {str(error)}"
        )
    except Exception as error:
        logging.error(
            f"A new error occurred while sending a message about the "
            f"new advertisement to {telegram_id}: {str(error)}"
        )


async def create_send_message_tasks(bot_instance: Bot, telegram_ids, adv_data: dict):
    """Create asyncio tasks and run them."""
    await asyncio.gather(
        *[
            send_telegram_message(bot_instance, telegram_id, adv_data)
            for telegram_id in telegram_ids
        ]
    )
