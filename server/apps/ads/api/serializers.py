from rest_framework import serializers

from server.apps.ads.choices import AdvertisementType


class MapAdvertisementsSerializer(serializers.Serializer):
    species = serializers.CharField(allow_null=True)
    type = serializers.ChoiceField(choices=AdvertisementType.choices)
    coords = serializers.ListField()
