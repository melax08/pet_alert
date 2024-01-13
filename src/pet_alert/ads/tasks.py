import asyncio
import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from telegram import Bot

from .utils import create_send_message_tasks

# from sorl.thumbnail import get_thumbnail, delete


User = get_user_model()


@shared_task
def send_information_about_new_advertisement(adv_data):
    """Celery task to send the information about a new advertisement to all
    staff users with telegram ids."""
    try:
        staff_with_telegram = list(
            User.objects.filter(is_staff=True, telegram_id__isnull=False).values(
                "telegram_id"
            )
        )

        if staff_with_telegram:
            bot = Bot(token=settings.TELEGRAM_TOKEN)
            asyncio.run(create_send_message_tasks(bot, staff_with_telegram, adv_data))

    except Exception as e:
        logging.error(str(e))
