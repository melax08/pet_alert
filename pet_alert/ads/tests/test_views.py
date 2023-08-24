import json
from http import HTTPStatus
from django.urls import reverse

from .fixtures import BaseTestCaseWithFixtures
from ..models import Lost, Found


class AdsViewTests(BaseTestCaseWithFixtures):
    FETCH_CONTENT_TYPE = 'application/json'

    def _test_open_close_ad(self, model, abbreviated):
        advertisement = model.objects.create(
            description='random description',
            author=self.user,
            type=self.animal_type,
            active=True,
            open=True
        )

        post_request_data = {'m': abbreviated, 'ad_id': advertisement.id}

        # Test closing the advertisement.
        response = self.authorized_client.post(
            reverse('ads:close_ad'),
            data=json.dumps(post_request_data),
            content_type=self.FETCH_CONTENT_TYPE
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        testing_advertisement = model.objects.get(pk=advertisement.id)
        self.assertFalse(testing_advertisement.open)

        # Test opening the advertisement.
        response = self.authorized_client.post(
            reverse('ads:open_ad'),
            data=json.dumps(post_request_data),
            content_type=self.FETCH_CONTENT_TYPE
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        testing_advertisement = model.objects.get(pk=advertisement.id)
        self.assertTrue(testing_advertisement.open)

    def test_open_close_lost_ad(self):
        """The user can close and open the lost ad with a fetch request."""
        self._test_open_close_ad(Lost, 'l')

    def test_open_close_found_ad(self):
        """The user can close and open the found ad with a fetch request."""
        self._test_open_close_ad(Found, 'f')

    def test_wrong_open_close_request(self):
        """The user can't break open/close view."""
        def __bad_id_request(abbreviated, url):
            response = self.authorized_client.post(
                url,
                data=json.dumps({'m': abbreviated, 'ad_id': 9999}),
                content_type=self.FETCH_CONTENT_TYPE
            )
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        # Request with non-existent ad_id returns a bad request
        # For Lost model, close ad:
        __bad_id_request('l', reverse('ads:close_ad'))
        # For Lost model, open ad:
        __bad_id_request('l', reverse('ads:open_ad'))
        # For Found model, close ad:
        __bad_id_request('f', reverse('ads:close_ad'))
        # For Found model, open ad:
        __bad_id_request('f', reverse('ads:open_ad'))

        # Non-existent abbreviation returns a bad request
        # For close ad:
        post_request_data = {
            'm': 'broken',
            'ad_id': self.lost_open_active_ad.id
        }
        response = self.authorized_client.post(
            reverse('ads:close_ad'),
            data=json.dumps(post_request_data),
            content_type=self.FETCH_CONTENT_TYPE
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertTrue(Lost.objects.get(pk=self.lost_open_active_ad.id).open)
        self.assertTrue(
            Found.objects.get(pk=self.found_open_active_ad.id).open
        )

        # For open ad:
        post_request_data = {
            'm': 'broken',
            'ad_id': self.lost_closed_inactive_ad.id
        }
        response = self.authorized_client.post(
            reverse('ads:open_ad'),
            data=json.dumps(post_request_data),
            content_type=self.FETCH_CONTENT_TYPE
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(
            Lost.objects.get(pk=self.lost_closed_inactive_ad.id).open
        )
        self.assertFalse(
            Found.objects.get(pk=self.found_closed_inactive_ad.id).open
        )



