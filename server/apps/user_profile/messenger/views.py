from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, View

from .constants import DIALOGS_PER_PAGE
from .forms import SendMessageForm
from .models import Dialog
from .services import MessengerService


class MessengerDialogListView(LoginRequiredMixin, ListView):
    """Shows the list of user chats."""

    template_name = "user_profile/messenger/messages_list.html"
    allow_empty = True
    paginate_by = DIALOGS_PER_PAGE
    context_object_name = "chats"

    def get_queryset(self) -> QuerySet[Dialog]:
        messenger_service = MessengerService(user=self.request.user)
        return messenger_service.get_dialogs()


class MessengerDialogDetailView(LoginRequiredMixin, View):
    """Show the messages in the dialog. The user can send a new message."""

    def get(self, request: HttpRequest, *args: Any, **kwarg: Any) -> HttpResponse:
        messenger_service = MessengerService(user=request.user)

        dialog = messenger_service.get_dialog(dialog_id=self.kwargs["dialog_id"])
        messenger_service.mark_dialog_messages_as_viewed(dialog)

        return render(
            request,
            "user_profile/messenger/messages_chat.html",
            {
                "messages": messenger_service.get_dialog_messages(dialog),
                "form": SendMessageForm(),
                "advertisement": dialog.advertisement_group,
            },
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        messenger_service = MessengerService(user=request.user)

        dialog = messenger_service.get_dialog(dialog_id=self.kwargs["dialog_id"])

        form = SendMessageForm(request.POST or None)
        if form.is_valid():
            messenger_service.send_message(form, dialog)

        return redirect("messenger:messages_chat", self.kwargs["dialog_id"])
