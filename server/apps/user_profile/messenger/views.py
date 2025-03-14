import json
from http import HTTPStatus
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, View

from server.apps.ads.exceptions import BadRequest
from server.apps.ads.models import Lost

# ToDo: move to core or refactor
from server.apps.ads.views import AuthFetchBase

from .constants import DIALOGS_PER_PAGE
from .forms import SendMessageForm
from .models import Dialog, Message
from .services import MessengerService


class DialogList(LoginRequiredMixin, ListView):
    """Shows the list of user chats."""

    template_name = "messenger/messages_list.html"
    allow_empty = True
    paginate_by = DIALOGS_PER_PAGE
    context_object_name = "chats"

    def get_queryset(self) -> QuerySet[Dialog]:
        messenger_service = MessengerService(user=self.request.user)
        return messenger_service.get_dialogs()


class MessageChat(LoginRequiredMixin, View):
    """Show the messages in the dialog. The user can send a new message."""

    def get(self, request: HttpRequest, *args: Any, **kwarg: Any) -> HttpResponse:
        messenger_service = MessengerService(user=request.user)

        dialog = messenger_service.get_dialog(dialog_id=self.kwargs["dialog_id"])
        messenger_service.mark_dialog_messages_as_viewed(dialog)

        return render(
            request,
            "messenger/messages_chat.html",
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


class DialogBase(AuthFetchBase):
    """Base class for dialog views."""

    @staticmethod
    def _get_dialog_ad_field(ad):
        return "advertisement_lost" if isinstance(ad, Lost) else "advertisement_found"


class GetDialog(DialogBase):
    """Fetch view for gets dialog if its exists."""

    def post(self, request):
        try:
            ad = self._get_advertisement(request)
        except BadRequest:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        try:
            dialog = Dialog.objects.get(
                author=ad.author,
                questioner=request.user,
                **{self._get_dialog_ad_field(ad): ad},
            )
            dialog_id = dialog.id
        except Dialog.DoesNotExist:
            dialog_id = None

        return JsonResponse({"dialog_id": dialog_id})


class CreateDialog(DialogBase):
    """Fetch view for create dialog when the first message sent."""

    def post(self, request):
        message = json.loads(request.body.decode()).get("msg").strip()
        if not message:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        try:
            ad = self._get_advertisement(request)
        except BadRequest:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        params = {self._get_dialog_ad_field(ad): ad}

        if Dialog.objects.filter(author=ad.author, questioner=request.user, **params).exists():
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        dialog = Dialog.objects.create(author=ad.author, questioner=request.user, **params)
        Message.objects.create(
            dialog=dialog, sender=request.user, recipient=ad.author, content=message
        )
        return JsonResponse({"dialog_id": dialog.id})
