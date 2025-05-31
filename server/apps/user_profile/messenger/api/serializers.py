from rest_framework import serializers


class DialogSerializer(serializers.Serializer):
    ad_id = serializers.IntegerField()


class DialogResponseSerializer(serializers.Serializer):
    dialog_id = serializers.IntegerField()


class DialogCreateSerializer(DialogSerializer):
    message = serializers.CharField()
