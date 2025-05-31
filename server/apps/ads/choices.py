from django.db.models import IntegerChoices, TextChoices


class AnimalConditionChoices(IntegerChoices):
    OK = 1, "Здоровое"
    SICK = 2, "Больное"
    CRITICAL = 3, "Критическое"


class AdvertisementType(TextChoices):
    LOST = "lost", "Потерялся"
    FOUND = "found", "Нашелся"
