from django.contrib import admin

from .models import Lost, Found, AnimalType


class LostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'active', 'pet_name', 'address', 'type')
    list_editable = ('active', 'type')
    search_fields = ('description', 'pet_name', 'address')
    list_filter = ('type',)
    empty_value_display = '-пусто-'


class FoundAdmin(admin.ModelAdmin):
    list_display = ('pk', 'active', 'condition', 'address', 'type')
    list_editable = ('active', 'type')
    search_fields = ('description', 'address')
    list_filter = ('type',)
    empty_value_display = '-пусто-'


class TypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


admin.site.register(Lost, LostAdmin)
admin.site.register(Found, FoundAdmin)
admin.site.register(AnimalType, TypeAdmin)
