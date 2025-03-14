from django.contrib import admin
from django.db.models import Count

from .models import Dialog, Message


class MessageInline(admin.TabularInline):
    model = Message
    readonly_fields = ("sender", "recipient", "content", "checked")

    def get_queryset(self, request):
        return self.model.objects.select_related("sender", "recipient")

    def has_add_permission(self, request, obj):
        return False


@admin.register(Dialog)
class DialogAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "author",
        "questioner",
        "advertisement_lost",
        "advertisement_found",
        "messages_count",
    )
    readonly_fields = ("author", "questioner", "advertisement_lost", "advertisement_found")
    inlines = (MessageInline,)

    def get_queryset(self, request):
        return self.model.objects.annotate(messages_count=Count("messages"))

    def messages_count(self, obj):
        return obj.messages_count


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("pk", "sender", "recipient", "content", "pub_date", "checked")
    search_fields = ("content",)
    list_filter = ("sender", "recipient", "dialog")
