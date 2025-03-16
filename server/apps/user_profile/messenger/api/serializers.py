from rest_framework import serializers

from server.apps.ads.choices import AdType


class DialogSerializer(serializers.Serializer):
    ad_id = serializers.IntegerField()
    ad_type = serializers.ChoiceField(choices=AdType.choices)


class DialogResponseSerializer(serializers.Serializer):
    dialog_id = serializers.IntegerField()


class DialogCreateSerializer(DialogSerializer):
    message = serializers.CharField()
