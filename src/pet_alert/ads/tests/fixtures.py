from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import AnimalType, Dialog, Found, Lost, Message

User = get_user_model()


class BaseTestCaseWithFixtures(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            email="testuser@example.ru", first_name="User1", phone="88005553535"
        )
        cls.another_user = User.objects.create_user(
            email="anothertestuser@example.ru", first_name="User2"
        )
        cls.animal_type = AnimalType.objects.create(name="Animal", slug="animal")
        cls.lost_open_active_ad = Lost.objects.create(
            address="Санкт-Петербург, территория Петропавловская крепость, 3Д",
            latitude=Decimal(59),
            longitude=Decimal(30),
            # image=...,
            description="Test lost description",
            age="5 years",
            active=True,
            open=True,
            pet_name="Barsik",
            type=cls.animal_type,
            author=cls.user,
        )

        cls.found_open_active_ad = Found.objects.create(
            address="Санкт-Петербург, территория Петропавловская крепость, 3Д",
            latitude=Decimal(59),
            longitude=Decimal(30),
            # image=...,
            description="Test found description",
            age="6 years",
            active=True,
            open=True,
            condition="OK",
            type=cls.animal_type,
            author=cls.user,
        )

        cls.lost_closed_active_ad = Lost.objects.create(
            description="Test lost closed description",
            type=cls.animal_type,
            author=cls.user,
            active=True,
            open=False,
        )

        cls.found_closed_active_ad = Found.objects.create(
            description="Test found closed description",
            type=cls.animal_type,
            author=cls.user,
            condition="OK",
            active=True,
            open=False,
        )

        cls.lost_open_inactive_ad = Lost.objects.create(
            description="Test lost inactive description",
            type=cls.animal_type,
            author=cls.user,
            active=False,
            open=True,
        )

        cls.found_open_inactive_ad = Found.objects.create(
            description="Test found inactive description",
            type=cls.animal_type,
            author=cls.user,
            condition="OK",
            active=False,
            open=True,
        )

        cls.lost_closed_inactive_ad = Lost.objects.create(
            description="Test lost inactive closed description",
            type=cls.animal_type,
            author=cls.user,
            active=False,
            open=False,
        )

        cls.found_closed_inactive_ad = Found.objects.create(
            description="Test found inactive closed description",
            type=cls.animal_type,
            author=cls.user,
            condition="OK",
            active=False,
            open=False,
        )
        cls.dialog = Dialog.objects.create(
            author=cls.user,
            questioner=cls.another_user,
            advertisement_lost=cls.lost_open_active_ad,
        )

        cls.message_1 = Message.objects.create(
            dialog=cls.dialog,
            sender=cls.another_user,
            recipient=cls.user,
            content="Тестовое сообщение",
        )

        cls.message_2 = Message.objects.create(
            dialog=cls.dialog,
            sender=cls.user,
            recipient=cls.another_user,
            content="Тестовый ответ на тестовое сообщение",
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
