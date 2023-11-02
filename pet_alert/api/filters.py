from django_filters import rest_framework as filters

from ads.models import AnimalType


class AdFilter(filters.FilterSet):
    """
    Filtering advertisements by animal type slug.
    Example: /?type=cats.
    """
    type = filters.ModelChoiceFilter(
        to_field_name='slug',
        queryset=AnimalType.objects.all()
    )
