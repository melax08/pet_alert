# Generated by Django 4.2.1 on 2023-05-24 13:46
import shutil
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations

MEDIA_DIR = Path(settings.MEDIA_ROOT)
ICONS_DIR = Path(settings.ANIMAL_ICONS_PATH)
DEFAULT_IMAGES_DIR = Path(settings.ANIMAL_DEFAULT_IMG_PATH)
STATIC_ICON_DIR = Path(settings.BASE_DIR) / "server/static/img/map_icons"
STATIC_DEFAULT_IMAGES_DIR = Path(settings.BASE_DIR) / "server/static/img/animal_types"

ANIMAL_SPECIES = [
    {
        "name": "другое",
        "slug": "other",
        "icon": str(ICONS_DIR / "other.png"),
        "default_image": str(DEFAULT_IMAGES_DIR / "other.jpg"),
    },
    {
        "name": "кот",
        "slug": "cats",
        "icon": str(ICONS_DIR / "cat.png"),
        "default_image": str(DEFAULT_IMAGES_DIR / "cat.jpg"),
    },
    {
        "name": "собака",
        "slug": "dogs",
        "icon": str(ICONS_DIR / "dog.png"),
        "default_image": str(DEFAULT_IMAGES_DIR / "dog.jpg"),
    },
]


def add_types(apps, schema_editor):
    """
    Data migration.
    Creates map icons dir and default images dir in MEDIA dir, copy necessary
    images from static dirs to new media dirs, then creates animal types from
    `ANIMAL_TYPES` dictionary.
    """
    icons_dir = MEDIA_DIR / ICONS_DIR
    default_images_dir = MEDIA_DIR / DEFAULT_IMAGES_DIR
    icons_dir.mkdir(parents=True, exist_ok=True)
    default_images_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(STATIC_ICON_DIR, icons_dir, dirs_exist_ok=True)
    shutil.copytree(STATIC_DEFAULT_IMAGES_DIR, default_images_dir, dirs_exist_ok=True)

    animal_species_model = apps.get_model("ads", "AnimalSpecies")
    for animal_type in ANIMAL_SPECIES:
        new_animal_type = animal_species_model(**animal_type)
        new_animal_type.save()


def remove_types(apps, schema_editor):
    """
    Remove migration.
    Removes all animal_types specified in dictionary `ANIMAL_TYPES` from
    database if it exists.
    """
    animal_species_model = apps.get_model("ads", "AnimalSpecies")
    for animal_type in ANIMAL_SPECIES:
        try:
            animal_species_model.objects.get(**animal_type).delete()
        except ObjectDoesNotExist:
            print(f"Warning: Animal type {animal_type.get('name')} doesn't exists. Skipped.")


class Migration(migrations.Migration):
    dependencies = [
        ("ads", "0002_initial"),
    ]

    operations = [migrations.RunPython(add_types, remove_types)]
