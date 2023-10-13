from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

CONDITIONS_OF_PET = [
    ('OK', 'Здоровое'),
    ('BD', 'Больное'),
    ('CR', 'Критическое')
]


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
        upload_to=settings.ANIMAL_ICONS_PATH,
        help_text='Иконка для вида животного, будет отображаться на карте.'
    )
    default_image = models.ImageField(
        'Изображение по умолчанию',
        upload_to=settings.ANIMAL_DEFAULT_IMG_PATH,
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
    open = models.BooleanField(
        'Открыто',
        default=True,
        help_text='Объявление открыто пользователем'
    )

    class Meta:
        ordering = ['-pub_date']
        indexes = [
            models.Index(fields=['active', 'open'])
        ]
        abstract = True

    def __str__(self):
        return self.description[:30]


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


class Dialog(models.Model):
    # ToDo: убрать автора диалога, брать еще через related_name по объявлению.
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dialog_ad_author',
        verbose_name='Автор объявления из диалога'
    )

    questioner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dialog_ad_questioner',
        verbose_name='Задающий вопросы'
    )

    advertisement_lost = models.ForeignKey(
        Lost,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Тип объявления: потерялся'
    )
    advertisement_found = models.ForeignKey(
        Found,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Тип объявления: нашелся'
    )

    class Meta:
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'

        constraints = [
            models.CheckConstraint(
                check=Q(
                    advertisement_lost__isnull=False,
                    advertisement_found=None) | Q(
                    advertisement_lost=None,
                    advertisement_found__isnull=False
                ),
                name='dialog_advertisement_constraint'
            )
        ]

    def __str__(self):
        return (
            f'Диалог между автором {self.author} '
            f'и задающим вопросы {self.questioner}'
        )

    @property
    def advertisement_group(self):
        if self.advertisement_lost_id is not None:
            return self.advertisement_lost
        if self.advertisement_found_id is not None:
            return self.advertisement_found
        raise AssertionError("Message doesn't have any advertisement group")


class Message(models.Model):
    dialog = models.ForeignKey(
        Dialog,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Диалог'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='send_messages',
        verbose_name='Отправитель'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Получатель'
    )
    content = models.TextField(
        'Содержимое сообщения'
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    checked = models.BooleanField(
        'Просмотрено?',
        default=False
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        indexes = [
            models.Index(
                fields=['recipient', 'checked'],
                name='recipient checked idx'
            )
        ]

    def __str__(self):
        return (f'От {self.sender.first_name} к {self.recipient.first_name}: '
                f'{self.content[:30]}')
