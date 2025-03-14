from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

from server.apps.ads.models import Found, Lost
from server.apps.core.models.mixins import TimeStampedModelMixin

User = get_user_model()


class Dialog(TimeStampedModelMixin, models.Model):
    """
    Dialog model for conversation purposes.
    When some user sends the first message on an advertisement page,
    a new dialog will be created.
    - author in dialog is the author of an advertisement.
    - questioner - the another user who sent a message to author of an advertisement.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dialogs_author",
        verbose_name="Автор объявления из диалога",
    )

    questioner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dialogs_questioner",
        verbose_name="Задающий вопросы",
    )

    advertisement_lost = models.ForeignKey(
        Lost,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Тип объявления: потерялся",
    )
    advertisement_found = models.ForeignKey(
        Found,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Тип объявления: нашелся",
    )

    class Meta:
        verbose_name = "Диалог"
        verbose_name_plural = "Диалоги"

        constraints = [
            models.CheckConstraint(
                check=Q(advertisement_lost__isnull=False, advertisement_found=None)
                | Q(advertisement_lost=None, advertisement_found__isnull=False),
                name="dialog_advertisement_constraint",
            )
        ]

    def __str__(self):
        return f"Диалог между автором {self.author} и задающим вопросы {self.questioner}"

    @property
    def advertisement_group(self):
        """Get the advertisement that bound to this dialog."""
        return self.advertisement_lost or self.advertisement_found


class Message(models.Model):
    """Message model that bound to some Dialog model."""

    dialog = models.ForeignKey(
        Dialog, on_delete=models.CASCADE, related_name="messages", verbose_name="Диалог"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="Отправитель",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
        verbose_name="Получатель",
    )
    content = models.TextField("Содержимое сообщения", max_length=500)
    pub_date = models.DateTimeField("Дата создания", auto_now_add=True)
    checked = models.BooleanField("Просмотрено?", default=False)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        indexes = [models.Index(fields=["recipient", "checked"], name="recipient checked idx")]

    def __str__(self):
        return f"От {self.sender.first_name} к {self.recipient.first_name}: {self.content[:30]}"
