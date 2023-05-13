from django import forms
from phonenumber_field.formfields import PhoneNumberField

from .models import Lost, Found


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

    class Meta:
        model = Lost
        fields = ('type', 'image', 'description', 'pet_name',
                  'age', 'first_name', 'phone', 'email')


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

    class Meta:
        model = Found
        fields = ('type', 'image', 'description', 'age', 'condition',
                  'first_name', 'phone', 'email')


class AuthorizedLostForm(forms.ModelForm):
    class Meta:
        model = Lost
        fields = ('type', 'image', 'description', 'pet_name', 'age')


class AuthorizedFoundForm(forms.ModelForm):
    class Meta:
        model = Found
        fields = ('type', 'image', 'description', 'age', 'condition')
