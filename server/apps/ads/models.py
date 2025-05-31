from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse_lazy
from polymorphic.models import PolymorphicModel
from sorl.thumbnail import get_thumbnail

from server.apps.core.models.mixins import TimeStampedModelMixin

from .choices import AdvertisementType, AnimalConditionChoices
from .constants import DESCRIPTION_MAP_LIMIT

User = get_user_model()


class AnimalSpecies(models.Model):
    """The animal species model. Used for filtering and to display default icons and images
    for various ads."""

    name = models.CharField(
        "Название вида",
        max_length=50,
        help_text="Укажите название вида животного",
        unique=True,
    )
    slug = models.SlugField(
        "Слаг", unique=True, help_text="Как будет называться вид животного в URL"
    )
    icon = models.ImageField(
        "Иконка",
        upload_to=settings.ANIMAL_ICONS_PATH,
        help_text="Иконка для вида животного, будет отображаться на карте.",
    )
    default_image = models.ImageField(
        "Изображение по умолчанию",
        upload_to=settings.ANIMAL_DEFAULT_IMG_PATH,
        help_text="Изображение для животного, которое будет отображаться по умолчанию.",
    )

    class Meta:
        verbose_name = "Вид животного"
        verbose_name_plural = "Виды животных"

    def __str__(self):
        return self.name


class Advertisement(TimeStampedModelMixin, PolymorphicModel):
    """Advertisement model with base fields for all kinds of advertisements."""

    address = models.CharField(
        "Адрес",
        max_length=300,
        help_text="Укажите адрес",
        blank=True,
    )
    latitude = models.DecimalField("Широта", max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(
        "Долгота", max_digits=9, decimal_places=6, blank=True, null=True
    )
    image = models.ImageField(
        "Фотография",
        upload_to="main/img",
        blank=True,
        help_text="Прикрепите фотографию питомца",
    )
    description = models.TextField("Описание", help_text="Опишите питомца")
    age = models.CharField(
        "Возраст животного",
        max_length=50,
        help_text="Примерный или точный возраст питомца",
        blank=True,
    )
    active = models.BooleanField(
        "Активно",
        default=False,
        help_text="Объявление одобрено, активно и видно на сайте.",
    )
    open = models.BooleanField(
        "Открыто", default=True, help_text="Объявление открыто пользователем"
    )

    species = models.ForeignKey(
        AnimalSpecies,
        on_delete=models.SET_NULL,
        related_name="advertisements",
        verbose_name="Вид животного",
        null=True,
        help_text="Выберите вид животного",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="advertisements",
        verbose_name="Автор объявления",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["active", "open"]),
            models.Index(fields=["active", "open", "latitude", "longitude"]),
        ]

    def __str__(self):
        return self.description[:30]

    @property
    def visible(self) -> bool:
        return self.active and self.open

    def _get_map_dict(self, header):
        """Get the dict with balloon information for yandex maps."""
        pet_name = getattr(self, "pet_name", "")
        hint_content = f"{header}: {pet_name}" if pet_name else header

        if self.image:
            small_img = get_thumbnail(self.image, "50x50", crop="center", quality=99)
            img = f'<img src="/media/{small_img}" class="rounded"'
            balloon_content_header = f"{img} <br> {hint_content}"
        else:
            balloon_content_header = hint_content

        if len(self.description) <= DESCRIPTION_MAP_LIMIT:
            balloon_content_body = self.description
        else:
            balloon_content_body = self.description[:DESCRIPTION_MAP_LIMIT] + "..."

        url = reverse_lazy("ads:advertisement_detail", kwargs={"ad_id": self.id})
        balloon_content_footer = f'<a href="{url}" target="_blank" class="pa-link">Перейти</a>'
        icon_href = f"/media/{self.species.icon}"

        return {
            "c": [self.latitude, self.longitude],
            "h": hint_content,
            "ch": balloon_content_header,
            "cb": balloon_content_body,
            "cf": balloon_content_footer,
            "i": icon_href,
        }


class Lost(Advertisement):
    """Model with information about lost animals."""

    pet_name = models.CharField(
        "Кличка", max_length=50, help_text="Кличка потерянного питомца", blank=True
    )

    class Meta(Advertisement.Meta):
        verbose_name = "Потерян"
        verbose_name_plural = "Потеряны"

    def get_map_dict(self):
        """Get the dict with balloon information for yandex maps."""
        return self._get_map_dict("Потерялся")


class Found(Advertisement):
    """Model with information about found animals."""

    condition = models.PositiveSmallIntegerField(
        "Состояние животного",
        choices=AnimalConditionChoices.choices,
        default=AnimalConditionChoices.OK,
        help_text="В каком состоянии было животное, когда вы его нашли?",
    )

    class Meta(Advertisement.Meta):
        verbose_name = "Найден"
        verbose_name_plural = "Найдены"

    def get_map_dict(self):
        """Get the dict with balloon information for yandex maps."""
        return self._get_map_dict("Нашелся")


ADVERTISEMENT_TYPES_LITERAL_MODEL_MAPPING: dict[str, type[Advertisement]] = {
    AdvertisementType.LOST: Lost,
    AdvertisementType.FOUND: Found,
}
