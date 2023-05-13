from django.db import models
from django.contrib.auth import get_user_model

from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

CONDITIONS_OF_PET = [
    ('OK', 'Здоровое'),
    ('BD', 'Больное'),
    ('CR', 'Критическое')
]

# ToDo: пол (мальчик, девочка, неопределен)
# ToDo: Цвет


class AnimalType(models.Model):
    name = models.CharField(
        'Название вида',
        max_length=50,
        help_text='Укажите название вида животного',
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        help_text='Как будет называться вид животного в URL'
    )
    icon = models.ImageField(
        'Иконка',
        upload_to='main/img/animal-icons',
        help_text='Иконка для вида животного, будет отображаться на карте.'
    )
    default_image = models.ImageField(
        'Изображение по умолчанию',
        upload_to='main/img/default-images',
        help_text=('Изображение для животного, '
                   'которое будет отображаться по умолчанию.')
    )

    class Meta:
        verbose_name = 'Вид животного'
        verbose_name_plural = 'Виды животных'

    def __str__(self):
        return self.name


class AdsAbstract(models.Model):
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    address = models.CharField(
        'Адрес',
        max_length=300,
        help_text='Укажите адрес где потеряли питомца',
        blank=True
    )
    coords = models.CharField(
        'Координаты',
        max_length=300,
        help_text='Координаты адреса',
        blank=True
    )
    image = models.ImageField(
        'Фотография',
        upload_to='main/img',
        blank=True,
        help_text='Прикрепите фотографию питомца'
    )
    description = models.TextField(
        'Описание',
        help_text='Опишите вашего потерянного питомца'
    )
    age = models.CharField(
        'Возраст питомца',
        max_length=50,
        help_text='Примерный или точный возраст животного',
        blank=True
    )
    active = models.BooleanField(
        'Активно',
        default=False,
        help_text='Объявление одобрено, активно и видно на сайте.'
    )

    class Meta:
        ordering = ['-pub_date']
        abstract = True

    def __str__(self):
        return self.description[:30]


# ToDo: сделать, чтобы help_text изменялся без переопределения поля.
class Lost(AdsAbstract):
    pet_name = models.CharField(
        'Кличка',
        max_length=50,
        help_text='Кличка потерянного питомца',
        blank=True
    )
    type = models.ForeignKey(
        AnimalType,
        on_delete=models.SET_NULL,
        related_name='lost',
        verbose_name='Вид животного',
        help_text='Выберите вид потерянного животного',
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lost_ads',
        verbose_name='Автор',
        help_text='Автор объявления о пропаже',
    )

    class Meta(AdsAbstract.Meta):
        verbose_name = 'Потерян'
        verbose_name_plural = 'Потеряны'


class Found(AdsAbstract):
    condition = models.CharField(
        'Состояние животного',
        max_length=2,
        choices=CONDITIONS_OF_PET,
        default='OK',
        help_text='В каком состоянии было животное, когда вы его нашли?'
    )
    image = models.ImageField(
        'Фотография',
        upload_to='main/img',
        blank=True,
        help_text='Прикрепите фотографию найденного животного'
    )
    description = models.TextField(
        'Описание',
        help_text='Опишите найденное животное'
    )
    age = models.CharField(
        'Примерный возраст',
        max_length=50,
        help_text='Примерный возраст животного',
        blank=True
    )
    type = models.ForeignKey(
        AnimalType,
        on_delete=models.SET_NULL,
        related_name='found',
        verbose_name='Вид животного',
        help_text='Выберите вид найденного животного',
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='found_ads',
        verbose_name='Автор',
        help_text='Автор объявления о находке',
    )

    class Meta(AdsAbstract.Meta):
        verbose_name = 'Найден'
        verbose_name_plural = 'Найдены'
