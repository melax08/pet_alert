from django import forms
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3, ReCaptchaV2Checkbox

from .models import Lost, Found, Message

User = get_user_model()


class BaseAddForm(forms.ModelForm):
    """
    Base form class for all add advertisement form. Only for inheritance.

    Features:
    - Replace empty label for animal type field.
    - Add form-control classes for all fields.
    - Add placeholders with label information for all fields.
    - Address and coords fields are hidden.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].empty_label = '- вид животного -'

        for visible in self.visible_fields():
            visible.field.widget.attrs[
                'class'] = 'form-control form-control-lg'
            visible.field.widget.attrs['placeholder'] = visible.field.label

    class Meta:
        widgets = {
            'address': forms.HiddenInput(),
            'coords': forms.HiddenInput()
        }


class LostForm(BaseAddForm):
    """Form for add lost advertisement with hidden user registration."""

    first_name = forms.CharField(
        label='Ваше имя',
        max_length=150,
        help_text='Ваше имя, будет видно в объявлениях и в личных сообщениях'
    )
    phone = PhoneNumberField(
        label='Номер мобильного телефона',
        help_text='Ваш номер телефона для связи',
        max_length=18
    )
    email = forms.EmailField(
        label='Электронная почта',
        max_length=254,
        help_text='Будет использоваться для логина на сайте'
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox,
        label='Подтвердите что вы не робот',
        help_text='Подтвердите что вы не робот'
    )

    class Meta(BaseAddForm.Meta):
        model = Lost
        fields = ('address', 'coords', 'type', 'image', 'description',
                  'pet_name', 'age', 'first_name', 'phone', 'email', 'captcha')


class FoundForm(LostForm):
    """Form for add found advertisement with hidden user registration."""
    class Meta(LostForm.Meta):
        model = Found
        fields = ('address', 'coords', 'type', 'image', 'description', 'age',
                  'condition', 'first_name', 'phone', 'email', 'captcha')


class AuthorizedLostForm(BaseAddForm):
    """Form for add lost advertisement for authorized users."""
    class Meta(BaseAddForm.Meta):
        model = Lost
        fields = ('address', 'coords', 'type', 'image', 'description',
                  'pet_name', 'age')


class AuthorizedFoundForm(BaseAddForm):
    """Form for add found advertisement for authorized users."""
    class Meta(BaseAddForm.Meta):
        model = Found
        fields = ('address', 'coords', 'type', 'image', 'description', 'age',
                  'condition')


class ChangeNameForm(forms.ModelForm):
    """Form for profile page, for change user info."""
    class Meta:
        model = User
        fields = ('first_name', )


class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content', )

        widgets = {
            'content': forms.Textarea(attrs={
                # 'rows': 6,
                'rows': 1,
                'placeholder': 'Введите сообщение'
            })
        }
