import random
import string

from ads.models import AnimalType, Lost
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

NUMBER_OF_ADS_TO_CREATE: int = 10000

User = get_user_model()


def _get_random_animal_type():
    return AnimalType.objects.get(id=random.randint(1, 3))


def _get_random_coords():
    return {
        "latitude": round(random.random() * random.randint(1, 179), 6),
        "longitude": round(random.random() * random.randint(1, 89), 6),
    }


def _get_random_age():
    return str(random.randint(1, 20))


def _get_random_string(x, y):
    return "".join(
        [
            "".join(random.choices(string.ascii_letters))
            for _ in range(random.randint(x, y))
        ]
    )


def _get_random_description():
    return _get_random_string(20, 50)


def _get_random_pet_name():
    return _get_random_string(3, 20)


class Command(BaseCommand):
    help = "Создает много объявлений с рандомными данными."

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--number_ads", type=int, default=NUMBER_OF_ADS_TO_CREATE
        )

    def handle(self, *args, **options):
        user = User.objects.create_user(
            email="stress@example.com",
            first_name="Stress",
            password="SomePass123",
            phone="+78005553535",
        )

        ads = []
        for _ in range(options["number_ads"]):
            ads.append(
                Lost(
                    address=_get_random_description(),
                    description=_get_random_description(),
                    age=_get_random_age(),
                    active=True,
                    open=True,
                    pet_name=_get_random_pet_name(),
                    type=_get_random_animal_type(),
                    author=user,
                    **_get_random_coords()
                )
            )
        Lost.objects.bulk_create(ads)
