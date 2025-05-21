import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from server.apps.ads.choices import AdType
from server.apps.ads.services import AdvertisementService
from server.apps.users.services import UserService

from .services import AdvertisementTelegramNotificationService

User = get_user_model()


@shared_task
def notify_staff_about_new_advertisement(adv_type: AdType, adv_id: int) -> None:
    """Celery task to send the information about a new advertisement to all
    staff users with telegram ids."""
    model = AdvertisementService.get_ad_model_by_ad_type(adv_type)
    advertisement = model.objects.filter(id=adv_id).select_related("author", "type").first()
    if not advertisement:
        logging.warning(f"Advertisement of model {adv_type} with id: {adv_id} was not found")
        return

    staff_telegram_ids = UserService.get_staff_telegram_ids()

    if staff_telegram_ids:
        service = AdvertisementTelegramNotificationService()
        service.send_advertisement_to_telegram_users(staff_telegram_ids, advertisement)
