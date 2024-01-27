from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Found, Lost
from .tasks import send_information_about_new_advertisement
from .utils import serialize_advertisement


@receiver(post_save, sender=Found)
@receiver(post_save, sender=Lost)
def post_save_advertisement(created, instance, **kwargs):
    """Create a new celery task after creation of a new advertisement."""
    if created:
        send_information_about_new_advertisement.delay(
            serialize_advertisement(instance)
        )
