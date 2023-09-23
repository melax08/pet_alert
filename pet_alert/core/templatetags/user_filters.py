from django import template
from django.conf import settings

register = template.Library()


@register.filter
def addclass(field, css):
    """Add specified custom css class to the field."""
    return field.as_widget(attrs={'class': css})


@register.filter
def getmodelname(obj):
    """Get the model name of this object."""
    return obj._meta.model_name


@register.filter
def addyamaps(obj):
    """
    Add yandex maps javascript code to the page.
    You need to fulfill .env file with:
    - YA_MAPS_API_KEY
    - YA_MAPS_SUGGEST_API_KEY
    You can find information about it in yandex maps API documentation.
    To use this filter, you need to create a stub variable in template,
    something like this:
    {{ stub_variable|addymaps|safe }}
    """
    maps_url_with_api_key = (
        f'https://api-maps.yandex.ru/2.1/?load=package.standard&lang=ru_RU'
        f'&amp;apikey={settings.YA_MAPS_API_KEY}'
        f'&suggest_apikey={settings.YA_MAPS_SUGGEST_API_KEY}'
    )

    return (f'<script async src="{maps_url_with_api_key}&onload=getYaMap" '
            f'type="text/javascript"></script>')
