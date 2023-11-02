from django.urls import reverse
from rest_framework import status
from rest_framework.test import override_settings

from .fixtures import BaseApiTestCaseWithFixtures, TEMP_MEDIA_ROOT
from ads.models import AnimalType


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class AdsApiTests(BaseApiTestCaseWithFixtures):

    def _check_response_status_codes(self, is_auth):
        """Checks compliance of response status codes for authorized user
        and anonymous user."""
        urls = {
            reverse('api:animal_type-list'):
                (status.HTTP_200_OK, status.HTTP_200_OK),
            reverse('api:animal_type-detail',
                    kwargs={'slug': self.animal_type.slug}):
                (status.HTTP_200_OK, status.HTTP_200_OK),
            reverse('api:lost-list'): (status.HTTP_200_OK, status.HTTP_200_OK),
            reverse('api:found-list'):
                (status.HTTP_200_OK, status.HTTP_200_OK),
            reverse('api:lost-detail',
                    kwargs={'pk': self.lost_open_active_ad.id}):
                (status.HTTP_200_OK, status.HTTP_200_OK),
            reverse('api:found-detail',
                    kwargs={'pk': self.found_open_active_ad.id}):
                (status.HTTP_200_OK, status.HTTP_200_OK),
            reverse('api:lost-detail',
                    kwargs={'pk': self.lost_closed_active_ad.id}):
                (status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
            reverse('api:found-detail',
                    kwargs={'pk': self.found_closed_active_ad.id}):
                (status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
            reverse('api:lost-detail',
                    kwargs={'pk': self.lost_open_inactive_ad.id}):
                (status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
            reverse('api:found-detail',
                    kwargs={'pk': self.found_open_inactive_ad.id}):
                (status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
            reverse('api:lost-detail',
                    kwargs={'pk': self.lost_closed_inactive_ad.id}):
                (status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
            reverse('api:found-detail',
                    kwargs={'pk': self.found_closed_inactive_ad.id}):
                (status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
        }

        client = self.author_client if is_auth else self.guest_client
        for url, status_code in urls.items():
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code[is_auth])

    def test_api_anonymous_user_requests(self):
        """Unauthorized user gets the right response codes
        with GET-requests."""
        self._check_response_status_codes(is_auth=False)

    def test_api_authorized_user_requests(self):
        """Authorized user gets the right response codes with
        GET-requests."""
        self._check_response_status_codes(is_auth=True)

    def test_api_another_user_requests_to_open_active_ads(self):
        """User get correct response code while trying to get another user
        ads."""
        urls_codes_map = {
            reverse('api:lost-detail',
                    kwargs={'pk': self.lost_open_active_ad.id}
                    ): status.HTTP_200_OK,
            reverse('api:found-detail',
                    kwargs={'pk': self.found_open_active_ad.id}
                    ): status.HTTP_200_OK,
            reverse('api:lost-detail',
                    kwargs={'pk': self.lost_closed_active_ad.id}
                    ): status.HTTP_404_NOT_FOUND,
            reverse('api:found-detail',
                    kwargs={'pk': self.found_closed_active_ad.id}
                    ): status.HTTP_404_NOT_FOUND,
            reverse('api:lost-detail',
                    kwargs={'pk': self.lost_open_inactive_ad.id}
                    ): status.HTTP_404_NOT_FOUND,
            reverse('api:found-detail',
                    kwargs={'pk': self.found_open_inactive_ad.id}
                    ): status.HTTP_404_NOT_FOUND,
            reverse('api:lost-detail',
                    kwargs={'pk': self.lost_closed_inactive_ad.id}
                    ): status.HTTP_404_NOT_FOUND,
            reverse('api:found-detail',
                    kwargs={'pk': self.found_closed_inactive_ad.id}
                    ): status.HTTP_404_NOT_FOUND
        }

        for url, status_code in urls_codes_map.items():
            with self.subTest(url=url):
                response = self.another_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_api_create_animal_type(self):
        """Only admin can create animal types."""
        animal_type_url = reverse('api:animal_type-list')
        animal_types_count_before = AnimalType.objects.count()

        animal_type_data = {
            "name": "Попугаи",
            "slug": "parrots",
            "icon": self.generate_image(),
            "default_image": self.generate_image()
        }

        # Admin can add new animal type
        admin_response = self.admin_client.post(
            animal_type_url,
            animal_type_data,
            format=self.FILES_FORMAT
        )
        self.assertEqual(admin_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            AnimalType.objects.count(),
            animal_types_count_before + 1
        )
        self.assertEqual(
            AnimalType.objects.last().slug,
            animal_type_data['slug']
        )

        # Anon can't create new animal type
        actual_animal_types_count = AnimalType.objects.count()
        animal_type_data['name'], animal_type_data['slug'] = 'Ящерицы', 'lizards'

        anon_response = self.guest_client.post(
            animal_type_url,
            animal_type_data,
            format=self.FILES_FORMAT
        )
        self.assertEqual(
            anon_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(actual_animal_types_count, AnimalType.objects.count())
        self.assertEqual(
            AnimalType.objects.last().slug,
            'parrots'
        )

        # User can't create new animal type
        actual_animal_types_count = AnimalType.objects.count()
        animal_type_data['name'], animal_type_data['slug'] = 'Птицы', 'birds'

        user_response = self.another_client.post(
            animal_type_url,
            animal_type_data,
            format=self.FILES_FORMAT
        )
        self.assertEqual(
            user_response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(actual_animal_types_count, AnimalType.objects.count())
        self.assertEqual(
            AnimalType.objects.last().slug,
            'parrots'
        )

    def test_api_patch_animal_type(self):
        """Only admin can modify animal type."""
        animal_type = AnimalType.objects.create(
            name='Кролики',
            slug='rabbits',
            icon=self.generate_image(),
            default_image=self.generate_image()
        )
        animal_type_url = reverse(
            'api:animal_type-detail',
            kwargs={'slug': animal_type.slug}
        )
        animal_types_count = AnimalType.objects.count()

        # Admin can patch animal type
        admin_response = self.admin_client.patch(
            animal_type_url,
            {'slug': 'monkeys'},
            format=self.DEFAULT_FORMAT
        )
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            AnimalType.objects.get(pk=animal_type.id).slug,
            'monkeys'
        )
        self.assertEqual(animal_types_count, AnimalType.objects.count())

        # User can't patch animal type
        user_response = self.another_client.patch(
            animal_type_url,
            {'slug': 'pigeons'},
            format=self.DEFAULT_FORMAT
        )
        self.assertEqual(user_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            AnimalType.objects.get(pk=animal_type.id).slug,
            'monkeys'
        )
        self.assertEqual(animal_types_count, AnimalType.objects.count())

        # Anonymous can't patch animal type
        anon_response = self.guest_client.patch(
            animal_type_url,
            {'slug': 'tigers'},
            format=self.DEFAULT_FORMAT
        )
        self.assertEqual(
            anon_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            AnimalType.objects.get(pk=animal_type.id).slug,
            'monkeys'
        )
        self.assertEqual(animal_types_count, AnimalType.objects.count())

