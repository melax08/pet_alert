import asyncio
import logging
from pathlib import Path

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError


def create_advertisement_message(adv_instance) -> dict:
    """Serialize Lost and Found advertisements to the dictionary."""
    try:
        image_path = adv_instance.image.path
    except ValueError:
        image_path = None

    message = (
        f"❗ Создано новое объявление!\n"
        f"<b>Автор</b>: {adv_instance.author.first_name}"
        f" ({adv_instance.author.email})\n"
        f"<b>Описание объявления</b>: {adv_instance.description}"
    )
    return {"image_path": image_path, "message": message}


async def send_telegram_message(bot_instance: Bot, telegram_id: int, adv_data: dict):
    """Sends the telegram message to the specified telegram user."""
    image_path = adv_data.get("image_path")
    message = adv_data.get("message")
    try:
        if image_path:
            await bot_instance.send_photo(
                telegram_id, Path(image_path), message, parse_mode=ParseMode.HTML
            )
        else:
            await bot_instance.send_message(
                telegram_id, message, parse_mode=ParseMode.HTML
            )
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
            send_telegram_message(bot_instance, item["telegram_id"], adv_data)
            for item in telegram_ids
        ]
    )
