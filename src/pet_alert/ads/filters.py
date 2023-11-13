import django_filters
from django import forms

from .models import AnimalType


class TypeFilter(django_filters.FilterSet):
    """Filter by animal type for advertisements."""

    type = django_filters.ModelChoiceFilter(
        queryset=AnimalType.objects.all(),
        field_name="type__name",
        to_field_name="slug",
        empty_label="Все животные",
        widget=forms.Select(attrs={"onchange": "submit();"}),
    )
