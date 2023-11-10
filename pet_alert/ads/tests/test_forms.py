from http import HTTPStatus
from django.urls import reverse
from django.test import Client
from django.contrib.auth.hashers import check_password
from django_registration.backends.activation.views import RegistrationView

from .fixtures import BaseTestCaseWithFixtures
from ..models import Lost, Found
from users.forms import CreationFormWithoutPassword
from users.models import User
from ads.forms import LostForm, FoundForm
from users.views import INTERNAL_SET_SESSION_TOKEN


# ToDo: проверить, что происходит при отправке почты.

class AdsFormsTests(BaseTestCaseWithFixtures):
    def test_creation_form_without_password(self):
        """Creation form without password works correct."""
        count_of_users = User.objects.count()

        form_data = {
            "first_name": "Валерий",
            "phone": "88005551012",
            "email": "valeriy@example.com"
        }

        form = CreationFormWithoutPassword(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        # While save the form with the valid data, create a new user
        # with empty password.
        form.save()
        self.assertEqual(User.objects.count(), count_of_users + 1)

        new_user = User.objects.last()
        self.assertEqual(new_user.email, form_data['email'])
        self.assertTrue(check_password('', new_user.password))

    def test_creation_form_without_password_wrong_email_phone(self):
        """The creation form work correct with wrong email and phone."""
        form_data = {
            "first_name": "Геральт",
            "phone": "123",
            "email": "email"
        }

        form = CreationFormWithoutPassword(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, 'email', errors='Введите правильный адрес электронной почты.'
        )
        self.assertFormError(
            form,
            'phone',
            errors=('Введите корректный номер телефона (например, 8 (301) '
                    '123-45-67) или номер с префиксом международной связи.')
        )

    def test_creation_form_without_password_used_email(self):
        """The creation form work correct with used email."""
        form_data = {
            "first_name": "Людовик",
            "phone": self.user.phone,
            "email": self.user.email
        }

        form = CreationFormWithoutPassword(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form,
            'email',
            errors=('Пользователь с таким Адрес электронной почты уже '
                    'существует.')
        )

    def _test_set_password_and_activate_user_with_empty_password(self, user):
        """
        User, who was registered by add new advertisement form (user without
        password and is_active=False) has to go by link in his email. After
        this, user has to set a new password for his account.
        """
        guest_client = Client()
        registration_view = RegistrationView()
        activation_key = registration_view.get_activation_key(user)
        guest_client.get(
            reverse(
                'users:registration_activate',
                kwargs={'activation_key': activation_key}
            ),
            follow=True
        )

        # Checks whether the client has the required parameter in the session
        # to set a new password
        self.assertTrue(guest_client.session.get(
            INTERNAL_SET_SESSION_TOKEN))

        new_password = 'PasPasPassWord!123'

        form_data = {
            'new_password1': new_password,
            'new_password2': new_password
        }

        # User successful set the password and activate his account.
        activation_response = guest_client.post(
            reverse(
                'users:registration_activate',
                kwargs={'activation_key': 'set-password'}
            ),
            data=form_data,
            follow=True
        )

        user.refresh_from_db()

        self.assertRedirects(
            activation_response, reverse('users:set_password_done')
        )

        self.assertTrue(user.is_active)
        self.assertTrue(check_password(new_password, user.password))
        # Auto login is working correctly.
        self.assertTrue(activation_response.context['user'].is_authenticated)

    def test_set_password_and_activate_new_user(self):
        """Set password for nonactive user without password works correct."""
        user = User.objects.create_user(
            email='nonpassworduser@example.com',
            password='',
            is_active=False,
            first_name='nonpassworduser'
        )
        self._test_set_password_and_activate_user_with_empty_password(user)

    def _test_add_advertisement_form_with_registration(
            self, model, model_form, add_advertisement_url, form_data
    ):
        """
        Guest user can create advertisement and register on a site at
        the same time.
        - Advertisement creates with active = False, open = True
        and author = new author.
        - User creates with is_active = False and without password.
        After registration, user has to go by link, that was sent to his email,
        and set a new password for his account.
        """
        ads_count_before = model.objects.count()
        users_count_before = User.objects.count()

        guest_client = Client()

        # Page with add advertisement form contains two forms
        # (for user creation and for advertisement creation).
        guest_response = guest_client.get(add_advertisement_url)
        self.assertTrue(
            isinstance(
                guest_response.context.get('form'),
                CreationFormWithoutPassword
            )
        )
        self.assertTrue(
            isinstance(
                guest_response.context.get('ad_form'),
                model_form
            )
        )

        guest_response = guest_client.post(
            add_advertisement_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(guest_response, reverse('ads:add_success_reg'))
        self.assertEqual(ads_count_before + 1, model.objects.count())
        self.assertEqual(users_count_before + 1, User.objects.count())

        # New user was correctly created.
        new_user = User.objects.last()
        self.assertTrue(User.objects.filter(
            email=form_data['email'],
            first_name=form_data['first_name']
        ).exists())
        self.assertTrue(check_password('', new_user.password))
        self.assertFalse(new_user.is_active)

        # New advertisement correctly created.
        new_advertisement = model.objects.filter(
                description=form_data['description'],
                author=new_user,
                address=form_data['address']
            )
        self.assertTrue(new_advertisement.exists())
        new_advertisement = new_advertisement.first()
        self.assertTrue(new_advertisement.open)
        self.assertFalse(new_advertisement.active)
        self.assertEqual(new_advertisement.author, new_user)

        # Continuation of registration work correctly.
        self._test_set_password_and_activate_user_with_empty_password(new_user)

    def test_lost_form_with_registration(self):
        """Lost advertisement created, user registered by unauthorized Lost
        advertisement form."""
        form_data = {
            'address': 'Санкт-Петербург, Звенигородская улица, 26',
            'latitude': 59.918296,
            'longitude': 30.341885,
            'type': self.animal_type.pk,
            'description': 'Потерял и регистрируюсь',
            'pet_name': 'Креветка',
            'first_name': 'Эдуард',
            'phone': '88005553530',
            'email': 'user2@example.com',
            'g-recaptcha-response': '123123123'
        }

        self._test_add_advertisement_form_with_registration(
            Lost,
            LostForm,
            reverse('ads:add_lost'),
            form_data
        )

    def test_found_form_with_registration(self):
        """Found advertisement created, user registered by unauthorized Lost
        advertisement form."""
        form_data = {
            'address': 'Санкт-Петербург, Звенигородская улица, 26',
            'latitude': 59.918296,
            'longitude': 30.341885,
            'type': self.animal_type.pk,
            'description': 'Нашел и регистрируюсь',
            'condition': 'OK',
            'first_name': 'Бен',
            'phone': '88005553571',
            'email': 'user3@example.com',
            'g-recaptcha-response': '123123123'
        }

        self._test_add_advertisement_form_with_registration(
            Found,
            FoundForm,
            reverse('ads:add_found'),
            form_data
        )

    def _test_add_advertisement_form(
            self, model, add_advertisement_url, form_data
    ):
        """Authorized user can create an advertisement."""
        ads_count_before = model.objects.count()
        users_count_before = User.objects.count()

        response = self.authorized_client.post(
            add_advertisement_url,
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('ads:add_success'))
        self.assertEqual(ads_count_before + 1, model.objects.count())
        self.assertEqual(users_count_before, User.objects.count())

        new_advertisement = model.objects.filter(
                description=form_data['description'],
                author=self.user,
                address=form_data['address']
            )
        self.assertTrue(new_advertisement.exists())
        new_advertisement = new_advertisement.first()
        self.assertTrue(new_advertisement.open)
        self.assertFalse(new_advertisement.active)
        self.assertEqual(new_advertisement.author, self.user)

    def test_lost_add_advertisement_form(self):
        """Lost advertisement form with authorized user works correct."""
        form_data = {
            'address': 'Санкт-Петербург, Кронштадт, Екатерининский парк',
            'latitude': 59.994768,
            'longitude': 29.769865,
            'type': self.animal_type.pk,
            'description': 'Потерял животное и я уже зареган',
            'pet_name': 'Бетон',
            'g-recaptcha-response': '123123123'
        }

        self._test_add_advertisement_form(
            Lost,
            reverse('ads:add_lost'),
            form_data
        )

    def test_found_add_advertisement_form(self):
        """Found advertisement form with authorized user works correct."""
        form_data = {
            'address': 'Санкт-Петербург, Кронштадт, Екатерининский парк',
            'latitude': 59.994768,
            'longitude': 29.769865,
            'type': self.animal_type.pk,
            'description': 'Нашел и я уже зареган',
            'condition': 'OK',
            'g-recaptcha-response': '123123123'
        }

        self._test_add_advertisement_form(
            Found,
            reverse('ads:add_found'),
            form_data
        )


