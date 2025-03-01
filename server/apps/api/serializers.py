from django.contrib.auth import get_user_model
from rest_framework import serializers

from server.apps.ads.models import AnimalType, Found, Lost

User = get_user_model()


class AnimalTypeSerializer(serializers.ModelSerializer):
    """Serializer for AnimalType model views."""

    class Meta:
        model = AnimalType
        fields = "__all__"


class AdsBaseSerializer(serializers.ModelSerializer):
    """Base serializer class for advertisement views."""

    author = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(), read_only=True
    )
    type = serializers.SlugRelatedField(slug_field="slug", queryset=AnimalType.objects.all())

    class Meta:
        read_only_fields = ("author", "pub_date", "id")


class LostAdListSerializer(AdsBaseSerializer):
    """
    Serializer for Lost advertisements view list actions.
    - Exclude active and open fields from response.
    """

    class Meta(AdsBaseSerializer.Meta):
        model = Lost
        exclude = ("active", "open")


class FoundAdListSerializer(LostAdListSerializer):
    """Serializer for Found advertisements view list actions."""

    class Meta(LostAdListSerializer.Meta):
        model = Found


class LostAdDetailSerializer(AdsBaseSerializer):
    """
    Serializer for Lost advertisements view detail actions.
    - Include all fields to response.
    """

    class Meta(AdsBaseSerializer.Meta):
        model = Lost
        fields = "__all__"
        read_only_fields = ("author", "pub_date", "id", "open", "active")


class FoundAdDetailSerializer(LostAdDetailSerializer):
    """Serializer for Found advertisements view detail actions."""

    class Meta(LostAdDetailSerializer.Meta):
        model = Found
