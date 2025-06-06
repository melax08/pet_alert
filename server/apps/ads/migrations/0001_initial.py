# Generated by Django 5.1.7 on 2025-05-28 08:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Advertisement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Дата создания"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата обновления")),
                (
                    "address",
                    models.CharField(
                        blank=True, help_text="Укажите адрес", max_length=300, verbose_name="Адрес"
                    ),
                ),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=9, null=True, verbose_name="Широта"
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=9,
                        null=True,
                        verbose_name="Долгота",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        help_text="Прикрепите фотографию питомца",
                        upload_to="main/img",
                        verbose_name="Фотография",
                    ),
                ),
                (
                    "description",
                    models.TextField(help_text="Опишите питомца", verbose_name="Описание"),
                ),
                (
                    "age",
                    models.CharField(
                        blank=True,
                        help_text="Примерный или точный возраст питомца",
                        max_length=50,
                        verbose_name="Возраст животного",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=False,
                        help_text="Объявление одобрено, активно и видно на сайте.",
                        verbose_name="Активно",
                    ),
                ),
                (
                    "open",
                    models.BooleanField(
                        default=True,
                        help_text="Объявление открыто пользователем",
                        verbose_name="Открыто",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AnimalType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Укажите название вида животного",
                        max_length=50,
                        unique=True,
                        verbose_name="Название вида",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="Как будет называться вид животного в URL",
                        unique=True,
                        verbose_name="Слаг",
                    ),
                ),
                (
                    "icon",
                    models.ImageField(
                        help_text="Иконка для вида животного, будет отображаться на карте.",
                        upload_to="main/img/animal-icons",
                        verbose_name="Иконка",
                    ),
                ),
                (
                    "default_image",
                    models.ImageField(
                        help_text="Изображение для животного, которое будет отображаться по умолчанию.",  # noqa
                        upload_to="main/img/default-images",
                        verbose_name="Изображение по умолчанию",
                    ),
                ),
            ],
            options={
                "verbose_name": "Вид животного",
                "verbose_name_plural": "Виды животных",
            },
        ),
        migrations.CreateModel(
            name="Found",
            fields=[
                (
                    "advertisement_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="ads.advertisement",
                    ),
                ),
                (
                    "condition",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "Здоровое"), (2, "Больное"), (3, "Критическое")],
                        default=1,
                        help_text="В каком состоянии было животное, когда вы его нашли?",
                        verbose_name="Состояние животного",
                    ),
                ),
            ],
            options={
                "verbose_name": "Найден",
                "verbose_name_plural": "Найдены",
                "abstract": False,
            },
            bases=("ads.advertisement",),
        ),
        migrations.CreateModel(
            name="Lost",
            fields=[
                (
                    "advertisement_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="ads.advertisement",
                    ),
                ),
                (
                    "pet_name",
                    models.CharField(
                        blank=True,
                        help_text="Кличка потерянного питомца",
                        max_length=50,
                        verbose_name="Кличка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Потерян",
                "verbose_name_plural": "Потеряны",
                "abstract": False,
            },
            bases=("ads.advertisement",),
        ),
    ]
