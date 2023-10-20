from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from ads.models import Lost, Found, AnimalType

User = get_user_model()
AUTH_TOKEN_PREFIX = 'Bearer'


class BaseApiTestCaseWithFixtures(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            email='author@example.com'
        )
        cls.user_admin = User.objects.create_user(
            email='admin@example.com'
        )
        cls.user_another = User.objects.create_user(
            email='another@example.com'
        )
        cls.user_author_token = RefreshToken.for_user(
            cls.user_author).access_token
        cls.user_admin_token = RefreshToken.for_user(
            cls.user_admin).access_token
        cls.user_another_token = RefreshToken.for_user(
            cls.user_another).access_token

        cls.animal_type = AnimalType.objects.create(
            name='Animal',
            slug='animal'
        )

        cls.lost_open_active_ad = Lost.objects.create(
            address='Санкт-Петербург, территория Петропавловская крепость, 3Д',
            latitude=Decimal(59),
            longitude=Decimal(30),
            # image=...,
            description='Test lost description',
            age='5 years',
            active=True,
            open=True,
            pet_name='Barsik',
            type=cls.animal_type,
            author=cls.user_author
        )

        cls.found_open_active_ad = Found.objects.create(
            address='Санкт-Петербург, территория Петропавловская крепость, 3Д',
            latitude=Decimal(59),
            longitude=Decimal(30),
            # image=...,
            description='Test found description',
            age='6 years',
            active=True,
            open=True,
            condition='OK',
            type=cls.animal_type,
            author=cls.user_author
        )

        cls.lost_closed_active_ad = Lost.objects.create(
            description='Test lost closed description',
            type=cls.animal_type,
            author=cls.user_author,
            active=True,
            open=False,
        )

        cls.found_closed_active_ad = Found.objects.create(
            description='Test found closed description',
            type=cls.animal_type,
            author=cls.user_author,
            condition='OK',
            active=True,
            open=False,
        )

        cls.lost_open_inactive_ad = Lost.objects.create(
            description='Test lost inactive description',
            type=cls.animal_type,
            author=cls.user_author,
            active=False,
            open=True,
        )

        cls.found_open_inactive_ad = Found.objects.create(
            description='Test found inactive description',
            type=cls.animal_type,
            author=cls.user_author,
            condition='OK',
            active=False,
            open=True,
        )

        cls.lost_closed_inactive_ad = Lost.objects.create(
            description='Test lost inactive closed description',
            type=cls.animal_type,
            author=cls.user_author,
            active=False,
            open=False,
        )

        cls.found_closed_inactive_ad = Found.objects.create(
            description='Test found inactive closed description',
            type=cls.animal_type,
            author=cls.user_author,
            condition='OK',
            active=False,
            open=False,
        )

    def setUp(self):
        self.guest_client = APIClient()
        self.author_client = APIClient()
        self.admin_client = APIClient()
        self.another_client = APIClient()

        self.author_client.credentials(
            HTTP_AUTHORIZATION=f'{AUTH_TOKEN_PREFIX} {self.user_author_token}'
        )
        self.admin_client.credentials(
            HTTP_AUTHORIZATION=f'{AUTH_TOKEN_PREFIX} {self.user_admin_token}'
        )
        self.another_client.credentials(
            HTTP_AUTHORIZATION=f'{AUTH_TOKEN_PREFIX} {self.user_another_token}'
        )
