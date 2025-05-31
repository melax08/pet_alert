from django.contrib import admin

from .models import AnimalSpecies, Found, Lost


@admin.register(Lost)
class LostAdmin(admin.ModelAdmin):
    list_display = ("pk", "active", "pet_name", "author", "address", "species")
    list_editable = ("active",)
    search_fields = ("description", "pet_name", "address")
    list_filter = ("species", "author")
    empty_value_display = "-пусто-"


@admin.register(Found)
class FoundAdmin(admin.ModelAdmin):
    list_display = ("pk", "active", "condition", "author", "address", "species")
    list_editable = ("active",)
    search_fields = ("description", "address")
    list_filter = ("species", "author", "condition")
    empty_value_display = "-пусто-"


@admin.register(AnimalSpecies)
class AnimalSpeciesAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
