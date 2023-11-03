from django.urls import reverse
from rest_framework import status
from rest_framework.test import override_settings

from .fixtures import BaseApiTestCaseWithFixtures, TEMP_MEDIA_ROOT
from ads.models import AnimalType, Lost, Found


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

    def _test_create_advertisement(self, url, request_data, model):
        advertisements_count = model.objects.count()

        # Guest user can't create an ad
        guest_response = self.guest_client.post(
            url,
            request_data,
            format=self.FILES_FORMAT
        )
        self.assertEqual(
            guest_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(model.objects.count(), advertisements_count)
        self.assertNotEqual(
            model.objects.first().description,
            request_data['description']
        )

        # Authorized user can create an ad
        request_data['image'] = self.generate_image()
        user_response = self.author_client.post(
            url,
            request_data,
            format=self.FILES_FORMAT
        )
        self.assertEqual(user_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(model.objects.count(), advertisements_count + 1)
        self.assertEqual(
            model.objects.first().description,
            request_data['description']
        )

        # Author of the new post is request user.
        self.assertEqual(model.objects.first().author, self.user_author)

        # New advertisement is open and nonactive.
        self.assertTrue(model.objects.first().open)
        self.assertFalse(model.objects.first().active)

    def test_api_create_lost(self):
        """Authorized user can create lost advertisements.
        Anonymous user can't create lost advertisements."""
        request_data = {
            'type': self.animal_type.slug,
            'description': 'Потерялось тестовое животное',
            'image': self.generate_image(),
            'address': 'Пушкина-Колотушкина',
            'latitude': 10,
            'longitude': 15,
            'age': '5 лет',
            'pet_name': 'Карасик'
        }

        self._test_create_advertisement(
            reverse('api:lost-list'),
            request_data,
            Lost
        )

    def test_api_create_found(self):
        """Authorized user can create found advertisements.
        Anonymous user can't create found advertisements."""
        request_data = {
            'type': self.animal_type.slug,
            'description': 'Нашлось тестовое животное',
            'image': self.generate_image(),
            'address': 'Пушкина-Колотушкина st, APT 2',
            'latitude': 5,
            'longitude': 20,
            'condition': 'OK',
            'age': '2 года',
        }

        self._test_create_advertisement(
            reverse('api:found-list'),
            request_data,
            Found
        )

    def _test_create_with_readonly_fields(self, url, model):
        request_data = {
            'description': 'Попытка задать readonly поля в объявлении',
            'type': self.animal_type.slug,
            'id': 666,
            'pub_date': 'время покушать',
            'author': self.user_another.id,
            'open': False,
            'active': True
        }

        self.author_client.post(
            url,
            request_data,
            format=self.DEFAULT_FORMAT
        )

        new_advertisement = model.objects.first()

        self.assertNotEqual(new_advertisement.author, self.another_client)
        self.assertNotEqual(new_advertisement.id, 666)
        self.assertNotEqual(new_advertisement.pub_date, 'время кушать')
        self.assertTrue(new_advertisement.open)
        self.assertFalse(new_advertisement.active)

    def test_create_with_readonly_fields_lost(self):
        """User can't set id, pub_date, author, open, active fields while
        create lost advertisement."""
        self._test_create_with_readonly_fields(reverse('api:lost-list'), Lost)

    def test_create_with_readonly_fields_found(self):
        """User can't set id, pub_date, author, open, active fields while
        create found advertisement."""
        self._test_create_with_readonly_fields(
            reverse('api:found-list'), Found)

    def _test_api_patch(self, reverse_url, model):
        new_advertisement = model.objects.create(
            author=self.user_author,
            type=self.animal_type,
            description='Тестовое животное для изменения',
        )
        request_url = reverse(
            reverse_url,
            kwargs={'pk': new_advertisement.pk}
        )
        advertisements_count = model.objects.count()

        # Anonymous can't modify an advertisement.
        new_description = 'Аноним попытался изменить объявление'
        guest_response = self.guest_client.patch(
            request_url,
            {'description': new_description}
        )

        self.assertEqual(
            guest_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertNotEqual(model.objects.first().description, new_description)
        self.assertEqual(advertisements_count, model.objects.count())

        # Author can't modify an advertisement.
        new_description = 'Автор объявления попытался его изменить'
        author_response = self.author_client.patch(
            request_url,
            {'description': new_description}
        )

        self.assertEqual(
            author_response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertNotEqual(model.objects.first().description, new_description)
        self.assertEqual(advertisements_count, model.objects.count())

        # Admin can modify an advertisement.
        new_description = 'Админ изменил описание объявления'
        admin_response = self.admin_client.patch(
            request_url,
            {'description': new_description}
        )

        self.assertEqual(
            admin_response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(model.objects.first().description, new_description)
        self.assertEqual(advertisements_count, model.objects.count())

    def test_api_patch_lost(self):
        """Only admin can modify lost advertisement."""
        self._test_api_patch('api:lost-detail', Lost)

    def test_api_patch_found(self):
        """Only admin can modify found advertisement."""
        self._test_api_patch('api:found-detail', Found)
