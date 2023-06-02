from django import forms
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3, ReCaptchaV2Checkbox

from .models import Lost, Found

User = get_user_model()


class LostForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Ваше имя',
        max_length=150,
        help_text='Ваше имя, будет видно в объявлениях и в личных сообщениях.'
    )
    phone = PhoneNumberField(
        label='Номер мобильного телефона',
        help_text='Ваш номер телефона для связи',
        max_length=18
    )
    email = forms.EmailField(
        label='Электронная почта',
        max_length=254,
        help_text='Будет использоваться для логина на сайте.'
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox,
        label='Подтвердите что вы не робот'
    )

    class Meta:
        model = Lost
        fields = ('address', 'coords', 'type', 'image', 'description',
                  'pet_name', 'age', 'first_name', 'phone', 'email', 'captcha')
        widgets = {
            'address': forms.HiddenInput(),
            'coords': forms.HiddenInput()
        }


class FoundForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Ваше имя',
        max_length=150,
        help_text='Ваше имя, будет видно в объявлениях и в личных сообщениях.'
    )
    phone = PhoneNumberField(
        label='Номер мобильного телефона',
        help_text='Ваш номер телефона для связи',
        max_length=18
    )
    email = forms.EmailField(
        label='Электронная почта',
        max_length=254,
        help_text='Будет использоваться для логина на сайте.'
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox,
        label='Подтвердите что вы не робот'
    )

    class Meta:
        model = Found
        fields = ('address', 'coords', 'type', 'image', 'description', 'age',
                  'condition', 'first_name', 'phone', 'email', 'captcha')
        widgets = {
            'address': forms.HiddenInput(),
            'coords': forms.HiddenInput()
        }


class AuthorizedLostForm(forms.ModelForm):
    class Meta:
        model = Lost
        fields = ('address', 'coords', 'type', 'image', 'description',
                  'pet_name', 'age')
        widgets = {
            'address': forms.HiddenInput(),
            'coords': forms.HiddenInput()
        }


class AuthorizedFoundForm(forms.ModelForm):
    class Meta:
        model = Found
        fields = ('address', 'coords', 'type', 'image', 'description', 'age',
                  'condition')
        widgets = {
            'address': forms.HiddenInput(),
            'coords': forms.HiddenInput()
        }


class ChangeNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', )
