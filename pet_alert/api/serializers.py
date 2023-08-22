from rest_framework import serializers

from ads.models import AnimalType  # noqa


class AnimalTypeSerializer(serializers.ModelSerializer):
    """Serializer for AnimalType model views."""

    class Meta:
        model = AnimalType
        fields = '__all__'
