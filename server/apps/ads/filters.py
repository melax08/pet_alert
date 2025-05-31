import django_filters
from django import forms

from .choices import AdvertisementType
from .models import AnimalSpecies, Found, Lost


class AdvertisementListFilterSet(django_filters.FilterSet):
    """Advertisements list filters."""

    species = django_filters.ModelChoiceFilter(
        queryset=AnimalSpecies.objects.all(),
        field_name="species__name",
        to_field_name="slug",
        empty_label="Все животные",
        widget=forms.Select(attrs={"onchange": "submit();"}),
    )

    type = django_filters.ChoiceFilter(
        method="filter_by_type", choices=AdvertisementType.choices, widget=forms.HiddenInput()
    )

    def filter_by_type(self, queryset, name, value):
        match value:
            case AdvertisementType.LOST:
                model = Lost
            case AdvertisementType.FOUND:
                model = Found
            case _:
                return queryset

        return queryset.instance_of(model)
