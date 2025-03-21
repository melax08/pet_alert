from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .tasks import send_mail_task


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with required email,
    email as username field and custom phone field."""

    objects = UserManager()
    username = None
    first_name = models.CharField(
        _("first name"),
        max_length=150,
        help_text="Ваше имя, будет видно в объявлениях и в личных сообщениях",
    )
    phone = PhoneNumberField(
        "Номер мобильного телефона",
        help_text="Ваш номер телефона для связи",
        max_length=18,
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        max_length=254,
        help_text="Будет использоваться для логина на сайте",
    )
    contact_email = models.BooleanField(
        "Показывать контактный email",
        default=False,
        help_text=("Показывать ли контактный email на страницах объявлений пользователя?"),
    )
    contact_phone = models.BooleanField(
        "Показывать контактный телефон",
        default=True,
        help_text=("Показывать ли контактный телефон на страницах объявлений пользователя?"),
    )
    telegram_id = models.PositiveIntegerField(
        "Telegram ID пользователя",
        null=True,
        blank=True,
        help_text="Используется для отправки сообщений пользователям в telegram",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta(AbstractUser.Meta):
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def is_empty_password(self):
        return check_password("", self.password)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send the email to this user via Celery."""
        send_mail_task.delay(subject, message, self.email, from_email, **kwargs)
