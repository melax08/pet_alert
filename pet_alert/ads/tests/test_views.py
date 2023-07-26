from http import HTTPStatus
from django.urls import reverse

from .fixtures import BaseTestCaseWithFixtures


class AdsViewTests(BaseTestCaseWithFixtures):

    def test_smoke(self):
        main_page = reverse('ads:index')
        guest_response = self.guest_client.get(main_page)
        authorized_response = self.authorized_client.get(main_page)
        self.assertEqual(guest_response.status_code, HTTPStatus.OK)
        self.assertEqual(authorized_response.status_code, HTTPStatus.OK)
