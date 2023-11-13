from django import template
from django.conf import settings
from django.core.paginator import Paginator

register = template.Library()


@register.filter
def addclass(field, css):
    """Add specified custom css class to the field."""
    return field.as_widget(attrs={"class": css})


@register.filter
def getmodelname(obj):
    """Get the model name of this object."""
    return obj._meta.model_name


@register.simple_tag
def addyamaps():
    """
    Add yandex maps javascript code to the page.
    You need to fulfill .env file with:
    - YA_MAPS_API_KEY
    - YA_MAPS_SUGGEST_API_KEY
    You can find information about it in yandex maps API documentation.
    To use this tag, you need to load this tag in your template with alias
    and use `safe` filter to it, like that:
    {% addyamaps as yamap %}
    {{ yamap|safe }}
    """
    maps_url_with_api_key = (
        f"https://api-maps.yandex.ru/2.1/?load=package.standard&lang=ru_RU"
        f"&amp;apikey={settings.YA_MAPS_API_KEY}"
        f"&suggest_apikey={settings.YA_MAPS_SUGGEST_API_KEY}"
    )

    return (
        f'<script async src="{maps_url_with_api_key}&onload=getYaMap" '
        f'type="text/javascript"></script>'
    )


@register.simple_tag
def get_proper_elided_page_range(p, number, on_each_side=3, on_ends=2):
    """
    Add template tag with elided pagination.
    Way to use in template:
    {% get_proper_elided_page_range paginator page_obj.number as page_range %}
    {% for i in page_range %}
      ... <-- Here is your pagination logic.
    {% endfor %}
    """
    paginator = Paginator(p.object_list, p.per_page)
    return paginator.get_elided_page_range(
        number=number, on_each_side=on_each_side, on_ends=on_ends
    )
