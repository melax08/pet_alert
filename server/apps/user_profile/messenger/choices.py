from django.db.models import TextChoices


class DialogConsumerActionTypeChoices(TextChoices):
    SEND_MESSAGE = "send_message", "Send message"
    READ_MESSAGES = "read_messages", "Read messages"
