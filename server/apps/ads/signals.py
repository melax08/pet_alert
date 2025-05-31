from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from server.apps.notifications.telegrams.tasks import notify_staff_about_new_advertisement

from .models import Found, Lost


@receiver(post_save, sender=Lost)
@receiver(post_save, sender=Found)
def post_save_advertisement(created: bool, instance: Lost | Found, **kwargs: Any) -> None:
    """Process some logic after creation of the new advertisement."""
    if created:
        notify_staff_about_new_advertisement.delay(instance.id)
