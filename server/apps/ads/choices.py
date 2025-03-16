from django.db.models import TextChoices

# ToDo: refactor to the integer choices
# from django.db.models import IntegerChoices

# class AdType(IntegerChoices):
#     LOST = 1, "Lost"
#     FOUND = 2, "Found"


class AdType(TextChoices):
    LOST = "l", "Lost"
    FOUND = "f", "Found"
