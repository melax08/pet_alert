from django.contrib import admin

from .models import Lost, Found


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


admin.site.register(Lost, LostAdmin)
admin.site.register(Found, FoundAdmin)
