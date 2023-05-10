import django_filters
from django import forms

from .models import Found, Lost, AnimalType


class TypeFilter(django_filters.FilterSet):
    type = django_filters.ModelChoiceFilter(
        queryset=AnimalType.objects.all(),
        field_name='type__name',
        to_field_name='slug',
        empty_label='Все животные',
        widget=forms.Select(attrs={'onchange': 'submit();'})
    )

    # class Meta:
    #     model = Lost
    #     fields = ['type']
