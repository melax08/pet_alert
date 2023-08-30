from django.contrib import admin

from .models import Lost, Found, AnimalType, Message, Dialog


class LostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'active', 'pet_name', 'author', 'address', 'type')
    list_editable = ('active',)
    search_fields = ('description', 'pet_name', 'address')
    list_filter = ('type', 'author')
    empty_value_display = '-пусто-'


class FoundAdmin(admin.ModelAdmin):
    list_display = ('pk', 'active', 'condition', 'author', 'address', 'type')
    list_editable = ('active',)
    search_fields = ('description', 'address')
    list_filter = ('type', 'author', 'condition')
    empty_value_display = '-пусто-'


class TypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'sender', 'recipient', 'content', 'pub_date', 'checked'
    )
    search_fields = ('content', )
    list_filter = ('sender', 'recipient', 'dialog')


class DialogAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'questioner', 'advertisement_lost',
                    'advertisement_found')


admin.site.register(Lost, LostAdmin)
admin.site.register(Found, FoundAdmin)
admin.site.register(AnimalType, TypeAdmin)
admin.site.register(Dialog, DialogAdmin)
admin.site.register(Message, MessageAdmin)
