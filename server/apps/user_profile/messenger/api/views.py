from django.db import transaction
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.ads.services import AdvertisementService
from server.apps.user_profile.messenger.models import Dialog, Message

from .serializers import DialogCreateSerializer, DialogResponseSerializer, DialogSerializer


class GetDialogView(APIView):
    """Get a dialog between the request user and the advertisement author."""

    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request: Request) -> Response:
        serializer = DialogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        advertisement_service = AdvertisementService()
        advertisement = advertisement_service.get_advertisement_or_404(
            ad_type=serializer.data.get("ad_type"), ad_id=serializer.data.get("ad_id")
        )

        dialog = Dialog.objects.filter(
            author=advertisement.author,
            questioner=request.user,
            **{advertisement.dialog_field_name: advertisement},
        ).first()
        dialog_id = dialog.id if dialog else None

        return Response(DialogResponseSerializer({"dialog_id": dialog_id}).data, status.HTTP_200_OK)


class CreateDialogView(APIView):
    """Get or create a dialog between the request user and the advertisement author and
    send specified message to the dialog."""

    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request: Request) -> Response:
        serializer = DialogCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        advertisement_service = AdvertisementService()
        advertisement = advertisement_service.get_advertisement_or_404(
            ad_type=serializer.data.get("ad_type"), ad_id=serializer.data.get("ad_id")
        )

        if advertisement_service.is_user_advertisement_author(advertisement, request.user):
            raise ValidationError({"error": "The user can't message himself"})

        with transaction.atomic():
            dialog, _ = Dialog.objects.get_or_create(
                author=advertisement.author,
                questioner=request.user,
                **{advertisement.dialog_field_name: advertisement},
            )

            Message.objects.create(
                dialog=dialog,
                sender=request.user,
                recipient=advertisement.author,
                content=serializer.data.get("message"),
            )

        return Response(DialogResponseSerializer({"dialog_id": dialog.id}).data, status.HTTP_200_OK)
