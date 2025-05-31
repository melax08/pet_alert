from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from server.apps.core.serializers import AdvertisementAPISerializer


class AdvertisementAPIView(APIView):
    """Base view for advertisements session API."""

    permission_classes = (AllowAny,)
    authentication_classes = (SessionAuthentication,)
    serializer = AdvertisementAPISerializer


class AuthAdvertisementAPIView(AdvertisementAPIView):
    """Base view for advertisements session API with auth."""

    permission_classes = (IsAuthenticated,)
