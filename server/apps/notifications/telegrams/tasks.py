import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from server.apps.ads.models import Advertisement
from server.apps.users.services import UserService

from .services import AdvertisementTelegramNotificationService

User = get_user_model()


@shared_task
def notify_staff_about_new_advertisement(advertisement_id: int) -> None:
    """Celery task to send the information about a new advertisement to all
    staff users with telegram ids."""
    advertisement = (
        Advertisement.objects.filter(id=advertisement_id)
        .select_related("author", "species")
        .first()
    )
    if not advertisement:
        logging.warning(f"Advertisement with id: {advertisement_id} was not found")
        return

    staff_telegram_ids = UserService.get_staff_telegram_ids()

    if staff_telegram_ids:
        service = AdvertisementTelegramNotificationService()
        service.send_advertisement_to_telegram_users(staff_telegram_ids, advertisement)
