from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django_registration.backends.activation.views import RegistrationView

from .fixtures import BaseTestCaseWithFixtures
from ..models import Lost, Found
from users.forms import CreationFormWithoutPassword
from users.models import User
from ads.forms import LostForm
from users.views import INTERNAL_SET_SESSION_TOKEN


class AdsFormsTests(BaseTestCaseWithFixtures):
    # print(form['phone'].errors)

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

    def test_lost_form_with_registration(self):
        """
        Guest user can create lost advertisement and register on a site at
        the same time.
        - Advertisement creates with active = False, open = True
        and author = new author.
        - User creates with is_active = False and without password.
        """
        ads_count_before = Lost.objects.count()
        users_count_before = User.objects.count()

        # Page with add advertisement form contains two forms
        # (for user creation and for advertisement creation).
        guest_response = self.guest_client.get(reverse('ads:add_lost'))
        self.assertTrue(
            isinstance(
                guest_response.context.get('form'),
                CreationFormWithoutPassword
            )
        )
        self.assertTrue(
            isinstance(
                guest_response.context.get('ad_form'),
                LostForm
            )
        )

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

        guest_response = self.guest_client.post(
            reverse('ads:add_lost'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(guest_response, reverse('ads:add_success_reg'))
        self.assertEqual(ads_count_before + 1, Lost.objects.count())
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
        new_advertisement = Lost.objects.filter(
                description=form_data['description'],
                pet_name=form_data['pet_name'],
                address=form_data['address']
            )
        self.assertTrue(new_advertisement.exists())
        new_advertisement = new_advertisement.first()
        self.assertTrue(new_advertisement.open)
        self.assertFalse(new_advertisement.active)
        self.assertEqual(new_advertisement.author, new_user)

        # Continuation of registration work correctly.

        # Get the activation key for the new user and make a response to
        # activate url with this key.
        registration_view = RegistrationView()
        activation_key = registration_view.get_activation_key(new_user)
        self.guest_client.get(
            reverse(
                'users:registration_activate',
                kwargs={'activation_key': activation_key}
            ),
            follow=True
        )

        # Check is client have a session to set password
        self.assertTrue(self.guest_client.session.get(
            INTERNAL_SET_SESSION_TOKEN))

        new_password = 'SomeHardPassword123'

        form_data = {
            'new_password1': new_password,
            'new_password2': new_password
        }

        # User successful set the password and activate his account.
        activation_response = self.guest_client.post(
            reverse(
                'users:registration_activate',
                kwargs={'activation_key': 'set-password'}
            ),
            data=form_data,
            follow=True
        )

        new_user.refresh_from_db()

        self.assertRedirects(
            activation_response, reverse('users:set_password_done')
        )

        self.assertTrue(new_user.is_active)
        self.assertTrue(check_password(new_password, new_user.password))
        # Auto login is working correct.
        self.assertTrue(activation_response.context['user'].is_authenticated)


        # ToDo: Перепроверить метод выше
        # ToDo: заменить guest_client на другого клиента, который будет только в этом методе
        # ToDo: Сделать ее универсальной и сделать проверку для Found объявлений
        # ToDo: разбить функцию на отдельные юнит тесты?
