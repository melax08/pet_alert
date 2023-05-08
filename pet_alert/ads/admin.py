from django.contrib import admin

from .models import Lost, Found, AnimalType


class LostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'active', 'pet_name', 'address', 'name', 'email')
    list_editable = ('active', )
    search_fields = ('description', 'pet_name', 'address')
    empty_value_display = '-пусто-'


class FoundAdmin(admin.ModelAdmin):
    list_display = ('pk', 'active', 'condition', 'address', 'name', 'email')
    list_editable = ('active',)
    search_fields = ('description', 'address')
    empty_value_display = '-пусто-'


class TypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'icon')


admin.site.register(Lost, LostAdmin)
admin.site.register(Found, FoundAdmin)
admin.site.register(AnimalType, TypeAdmin)
