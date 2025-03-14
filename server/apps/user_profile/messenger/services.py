from django.db.models import Count, OuterRef, Q, QuerySet, Subquery
from django.http import Http404
from django.shortcuts import get_object_or_404

from server.apps.users.models import User

from .forms import SendMessageForm
from .models import Dialog, Message


class MessengerService:
    def __init__(self, user: User) -> None:
        self._user = user

    def get_dialogs(self) -> QuerySet[Dialog]:
        latest_message_pubdate = (
            Message.objects.filter(dialog=OuterRef("pk"))
            .order_by("-pub_date")
            .values("pub_date")[:1]
        )

        latest_message_content = (
            Message.objects.filter(dialog=OuterRef("pk"))
            .order_by("-pub_date")
            .values("content")[:1]
        )

        return (
            Dialog.objects.select_related(
                "author",
                "questioner",
                "advertisement_lost",
                "advertisement_found",
                "advertisement_lost__type",
                "advertisement_found__type",
            )
            .filter(Q(author=self._user) | Q(questioner=self._user))
            .annotate(
                latest_message_date=Subquery(latest_message_pubdate),
                latest_message_content=Subquery(latest_message_content),
                unread_messages=Count(
                    "messages",
                    filter=Q(messages__recipient=self._user, messages__checked=False),
                ),
            )
            .order_by("-latest_message_date")
        )

    def get_dialog(self, dialog_id: int) -> Dialog:
        """Get dialog by its id. The user should be dialog author or dialog questioner to has
        access to the dialog."""
        dialog = get_object_or_404(
            Dialog.objects.select_related(
                "author",
                "questioner",
                "advertisement_lost__author",
                "advertisement_found__author",
                "advertisement_lost__type",
                "advertisement_found__type",
            ),
            pk=dialog_id,
        )

        if not (dialog.author == self._user or dialog.questioner == self._user):
            raise Http404

        return dialog

    @staticmethod
    def get_dialog_messages(dialog: Dialog) -> QuerySet[Message]:
        """Get all messages from the dialog."""
        return dialog.messages.prefetch_related("sender", "recipient").order_by("pub_date")

    def mark_dialog_messages_as_viewed(self, dialog: Dialog) -> None:
        """Set all unchecked messages in the dialog as viewed for the current user."""
        dialog.messages.filter(recipient=self._user, checked=False).update(checked=True)

    def send_message(self, form: SendMessageForm, dialog: Dialog) -> None:
        """Send the message from the current user to the another dialog member."""
        message = form.save(commit=False)
        message.dialog = dialog
        message.sender = self._user
        message.recipient = dialog.author if dialog.author != self._user else dialog.questioner
        message.save()
