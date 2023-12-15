from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_mail_task(subject, message, user_email, from_email=None, **kwargs):
    send_mail(subject, message, from_email, [user_email], **kwargs)
