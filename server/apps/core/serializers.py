from rest_framework import serializers


class AdvertisementAPISerializer(serializers.Serializer):
    ad_id = serializers.IntegerField()
