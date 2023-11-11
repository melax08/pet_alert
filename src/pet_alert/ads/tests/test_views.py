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

    def _test_context(self, response_obj, expected_obj):
        """Gets all class attrs from the first context page object, compares
        attrs of the first page object and the expected model object."""
        context_fields = {
            getattr(response_obj, attr): getattr(expected_obj, attr, None)
            for attr in expected_obj.__dict__ if attr != '_state'
        }

        for field, expected in context_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_lost_list_context(self):
        """Lost ads list page has correct context."""
        response = self.authorized_client.get(reverse('ads:lost'))
        self._test_context(
            response.context['page_obj'][0],
            self.lost_open_active_ad
        )

    def test_found_list_context(self):
        """Found ads list page has correct context."""
        response = self.authorized_client.get(reverse('ads:found'))
        self._test_context(
            response.context['page_obj'][0],
            self.found_open_active_ad
        )

    def test_lost_detail_context(self):
        """Lost ad detail page has correct context."""
        response = self.authorized_client.get(
            reverse(
                'ads:lost_detail',
                kwargs={'ad_id': self.lost_open_active_ad.id}
            )
        )
        self._test_context(
            response.context.get('ad'),
            self.lost_open_active_ad
        )

    def test_found_detail_context(self):
        """Found ad detail page has correct context."""
        response = self.authorized_client.get(
            reverse(
                'ads:found_detail',
                kwargs={'ad_id': self.found_open_active_ad.id}
            )
        )
        self._test_context(
            response.context.get('ad'),
            self.found_open_active_ad
        )

    def test_profile_active_context(self):
        """Profile active page has correct context."""
        response = self.authorized_client.get(reverse('ads:my_ads'))
        self._test_context(
            response.context['page_obj'][0],
            self.found_open_active_ad
        )

    def test_profile_inactive_context(self):
        """Profile inactive page has correct context."""
        response = self.authorized_client.get(reverse('ads:my_ads_inactive'))
        self._test_context(
            response.context['page_obj'][0],
            self.found_closed_inactive_ad
        )

    def test_index_context(self):
        """Index page has correct context."""
        response = self.authorized_client.get(reverse('ads:index'))
        self._test_context(
            response.context['losts'][0],
            self.lost_open_active_ad
        )
        self._test_context(
            response.context['founds'][0],
            self.found_open_active_ad
        )

    def test_dialog_list_context(self):
        """Dialog list page has correct context."""
        response = self.authorized_client.get(reverse('ads:messages'))
        self._test_context(
            response.context['chats'][0],
            self.dialog
        )
        self.assertEqual(1, response.context['chats'][0].unread_messages)
        self.assertEqual(
            response.context['chats'][0].messages.last().pub_date,
            response.context['chats'][0].latest_message_date
        )

    def test_dialog_detail_context(self):
        """Dialog detail page has correct context."""
        response = self.authorized_client.get(
            reverse(
                'ads:messages_chat',
                kwargs={'dialog_id': self.dialog.id}
            )
        )

        self._test_context(
            response.context['messages'][1],
            self.message_2
        )
