from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AdsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(email='testuser@example.ru')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(AdsViewTests.user)

    def test_smoke(self):
        main_page = reverse('ads:index')
        guest_response = self.guest_client.get(main_page)
        authorized_response = self.authorized_client.get(main_page)
        self.assertEqual(guest_response.status_code, HTTPStatus.OK)
        self.assertEqual(authorized_response.status_code, HTTPStatus.OK)
