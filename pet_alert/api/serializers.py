from rest_framework import serializers

from ads.models import AnimalType, Lost, Found  # noqa


class AnimalTypeSerializer(serializers.ModelSerializer):
    """Serializer for AnimalType model views."""

    class Meta:
        model = AnimalType
        fields = '__all__'


class LostAdSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='email',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    type = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=AnimalType.objects.all()
    )

    class Meta:
        model = Lost
        fields = '__all__'
        read_only_fields = ('author', 'active', 'open', 'pub_date', 'id')


class FoundAdSerializer(LostAdSerializer):

    class Meta(LostAdSerializer.Meta):
        model = Found
