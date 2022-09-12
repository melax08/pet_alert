from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CONDITIONS_OF_PET = [
    ('OK', 'Здоровое'),
    ('BD', 'Больное'),
    ('CR', 'Критическое')
]


class Lost(models.Model):
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    location = models.CharField(
        'Локация',
        max_length=100,
        help_text='Укажите где вы потеряли питомца'
    )
    image = models.ImageField(
        'Фотография',
        upload_to='ads/img',
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

    def __str__(self):
        return self.description[:15]


class Found(models.Model):
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    location = models.CharField(
        'Локация',
        max_length=100,
        help_text='Укажите где вы нашли животное'
    )
    image = models.ImageField(
        'Фотография',
        upload_to='ads/img',
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
    condition = models.CharField(
        'Состояние животного',
        max_length=2,
        choices=CONDITIONS_OF_PET,
        default='OK'
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

    def __str__(self):
        return self.description[:15]
