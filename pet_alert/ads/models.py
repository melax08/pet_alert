from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CONDITIONS_OF_PET = [
    ('OK', 'Здоровое'),
    ('BD', 'Больное'),
    ('CR', 'Критическое')
]

# ToDo: пол (мальчик, девочка, неопределен)
# ToDo: Цвет


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
    name = models.CharField(
        'Ваше имя',
        max_length=50
    )
    phone = models.CharField(
        'Номер телефона',
        max_length=20,
        help_text='Ваш номер телефона для связи',
        blank=True
    )
    email = models.EmailField(
        'Электронная почта',
        help_text='Ваша электронная почта для связи',
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
        return self.description[:15]


# ToDo: сделать, чтобы help_text изменялся без переопределения поля.
class Lost(AdsAbstract):
    pet_name = models.CharField(
            'Кличка',
            max_length=50,
            help_text='Кличка потерянного питомца',
            blank=True
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

    class Meta(AdsAbstract.Meta):
        verbose_name = 'Найден'
        verbose_name_plural = 'Найдены'
