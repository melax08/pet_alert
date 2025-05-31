from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.ads.api.serializers import MapAdvertisementsSerializer
from server.apps.ads.models import ADVERTISEMENT_TYPES_LITERAL_MODEL_MAPPING, Advertisement
from server.apps.ads.services import AdvertisementService
from server.apps.core.views.base import AdvertisementAPIView, AuthAdvertisementAPIView


class GetContactInfoView(AuthAdvertisementAPIView):
    """Get the author contact information for the advertisement."""

    def post(self, request: Request) -> Response:
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        advertisement_service = AdvertisementService()
        advertisement = advertisement_service.get_advertisement_or_404(
            ad_id=serializer.data.get("ad_id")
        )

        if not advertisement.visible and not advertisement_service.is_user_advertisement_author(
            advertisement, request.user
        ):
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            advertisement_service.get_advertisement_author_contact_info(advertisement),
            status.HTTP_200_OK,
        )


class OpenAdvertisementView(AuthAdvertisementAPIView):
    """Open the advertisement if the user is the author of the advertisement."""

    @staticmethod
    def finalize(advertisement_service: AdvertisementService, advertisement: Advertisement) -> None:
        advertisement_service.open_advertisement(advertisement)

    def post(self, request: Request) -> Response:
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        advertisement_service = AdvertisementService()
        advertisement = advertisement_service.get_advertisement_or_404(
            ad_id=serializer.data.get("ad_id")
        )

        if not advertisement_service.is_user_advertisement_author(advertisement, request.user):
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        self.finalize(advertisement_service, advertisement)

        return Response({"success": True}, status=status.HTTP_200_OK)


class CloseAdvertisementView(OpenAdvertisementView):
    """Close the advertisement if the user is the author of the advertisement."""

    @staticmethod
    def finalize(advertisement_service: AdvertisementService, advertisement: Advertisement) -> None:
        advertisement_service.close_advertisement(advertisement)


class MapAdvertisementsView(AdvertisementAPIView):
    """Get advertisements with specified map coordinates."""

    def post(self, request: Request) -> Response:
        serializer = MapAdvertisementsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            model = ADVERTISEMENT_TYPES_LITERAL_MODEL_MAPPING[serializer.data["type"]]
            min_x, min_y = serializer.data["coords"][0]
            max_x, max_y = serializer.data["coords"][1]
            animal_species = serializer.data["species"]
        except (KeyError, IndexError):
            return Response({}, status.HTTP_400_BAD_REQUEST)

        additional_params = {}
        if animal_species:
            additional_params["species__slug"] = animal_species

        advertisements = model.objects.prefetch_related("species").filter(
            active=True,
            open=True,
            latitude__gte=min_x,
            latitude__lte=max_x,
            longitude__gte=min_y,
            longitude__lte=max_y,
            **additional_params,
        )

        data = [ad.get_map_dict() for ad in advertisements]

        return Response(data, status=status.HTTP_200_OK)
