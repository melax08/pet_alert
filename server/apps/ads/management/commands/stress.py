import random
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from server.apps.ads.models import AnimalType, Lost

NUMBER_OF_ADS_TO_CREATE: int = 10000

User = get_user_model()


class Command(BaseCommand):
    help = "Создает много Lost объявлений с рандомными данными."

    @staticmethod
    def _get_random_animal_type():
        return AnimalType.objects.get(id=random.randint(1, 3))

    @staticmethod
    def _get_random_coords():
        return {
            "latitude": round(random.randint(59, 60) + random.random(), 6),
            "longitude": round(random.randint(29, 30) + random.random(), 6),
        }

    @staticmethod
    def _get_random_age():
        return str(random.randint(1, 20))

    @staticmethod
    def _get_random_string(x, y):
        return "".join(
            ["".join(random.choices(string.ascii_letters)) for _ in range(random.randint(x, y))]
        )

    def _get_random_description(self):
        return self._get_random_string(20, 50)

    def _get_random_pet_name(self):
        return self._get_random_string(3, 20)

    def add_arguments(self, parser):
        parser.add_argument("-n", "--number_ads", type=int, default=NUMBER_OF_ADS_TO_CREATE)

    def handle(self, *args, **options):
        if not settings.DJANGO_ENV == "development":
            raise CommandError(
                "You can't use stress command in production! "
                "You need to set env DJANGO_ENV=development before using this command."
            )

        stress_user_email = "stress@example.com"
        user = User.objects.filter(email=stress_user_email)

        if user.exists():
            user = user.first()
        else:
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
                    address=self._get_random_description(),
                    description=self._get_random_description(),
                    age=self._get_random_age(),
                    active=True,
                    open=True,
                    pet_name=self._get_random_pet_name(),
                    type=self._get_random_animal_type(),
                    author=user,
                    **self._get_random_coords(),
                )
            )
        Lost.objects.bulk_create(ads)
