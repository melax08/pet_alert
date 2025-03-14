from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse_lazy
from sorl.thumbnail import get_thumbnail

from .constants import DESCRIPTION_MAP_LIMIT

User = get_user_model()

CONDITIONS_OF_PET = [("OK", "Здоровое"), ("BD", "Больное"), ("CR", "Критическое")]
MAP_IMAGE_QUALITY = 99


class AnimalType(models.Model):
    """The kind of animal. Used for filtering and to display default icons and images
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
        help_text=("Изображение для животного, которое будет отображаться по умолчанию."),
    )

    class Meta:
        verbose_name = "Вид животного"
        verbose_name_plural = "Виды животных"

    def __str__(self):
        return self.name


class AdsAbstract(models.Model):
    """Abstract class with common field for Lost and Found advertisements."""

    pub_date = models.DateTimeField("Дата создания объявления", auto_now_add=True)
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
    description = models.TextField("Описание", help_text="Опишите вашего потерянного питомца")
    age = models.CharField(
        "Возраст питомца",
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

    class Meta:
        ordering = ["-pub_date"]
        indexes = [
            models.Index(fields=["active", "open"]),
            models.Index(fields=["active", "open", "latitude", "longitude"]),
        ]
        abstract = True

    def __str__(self):
        return self.description[:30]

    def _get_map_dict(self, reverse_url, header):
        """Get the dict with balloon information for yandex maps."""
        pet_name = getattr(self, "pet_name", "")
        if pet_name:
            hint_content = f"{header}: {pet_name}"
        else:
            hint_content = header

        if self.image:
            small_img = get_thumbnail(self.image, "50x50", crop="center", quality=MAP_IMAGE_QUALITY)
            img = f'<img src="/media/{small_img}" class="rounded"'
            balloon_content_header = f"{img} <br> {hint_content}"
        else:
            balloon_content_header = hint_content

        if len(self.description) <= DESCRIPTION_MAP_LIMIT:
            balloon_content_body = self.description
        else:
            balloon_content_body = self.description[:DESCRIPTION_MAP_LIMIT] + "..."

        url = reverse_lazy(reverse_url, kwargs={"ad_id": self.id})
        balloon_content_footer = f'<a href="{url}" target="_blank" class="pa-link">Перейти</a>'
        icon_href = f"/media/{self.type.icon}"

        return {
            "c": [self.latitude, self.longitude],
            "h": hint_content,
            "ch": balloon_content_header,
            "cb": balloon_content_body,
            "cf": balloon_content_footer,
            "i": icon_href,
        }


class Lost(AdsAbstract):
    """
    Model for Lost advertisements.
    Fields that only this ad type has:
    - pet_name.
    """

    pet_name = models.CharField(
        "Кличка", max_length=50, help_text="Кличка потерянного питомца", blank=True
    )
    type = models.ForeignKey(
        AnimalType,
        on_delete=models.SET_NULL,
        related_name="lost",
        verbose_name="Вид животного",
        help_text="Выберите вид потерянного питомца",
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lost_ads",
        verbose_name="Автор",
        help_text="Автор объявления о пропаже",
    )

    class Meta(AdsAbstract.Meta):
        verbose_name = "Потерян"
        verbose_name_plural = "Потеряны"

    def get_map_dict(self):
        """Get the dict with balloon information for yandex maps."""
        return self._get_map_dict("ads:lost_detail", "Потерялся")


class Found(AdsAbstract):
    """
    Model for Found advertisements.
    Fields that only this ad type has:
    - condition.
    """

    condition = models.CharField(
        "Состояние животного",
        max_length=2,
        choices=CONDITIONS_OF_PET,
        default="OK",
        help_text="В каком состоянии было животное, когда вы его нашли?",
    )
    image = models.ImageField(
        "Фотография",
        upload_to="main/img",
        blank=True,
        help_text="Прикрепите фотографию найденного животного",
    )
    description = models.TextField("Описание", help_text="Опишите найденное животное")
    age = models.CharField(
        "Примерный возраст",
        max_length=50,
        help_text="Примерный возраст животного",
        blank=True,
    )
    type = models.ForeignKey(
        AnimalType,
        on_delete=models.SET_NULL,
        related_name="found",
        verbose_name="Вид животного",
        help_text="Выберите вид найденного животного",
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="found_ads",
        verbose_name="Автор",
        help_text="Автор объявления о находке",
    )

    class Meta(AdsAbstract.Meta):
        verbose_name = "Найден"
        verbose_name_plural = "Найдены"

    def get_map_dict(self):
        """Get the dict with balloon information for yandex maps."""
        return self._get_map_dict("ads:found_detail", "Нашелся")
