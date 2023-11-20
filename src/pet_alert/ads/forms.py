from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField

from .constants import ROWS_IN_DIALOG_MESSAGE_FORM
from .models import Found, Lost, Message

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
        self.fields["type"].empty_label = "- вид животного -"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control form-control-lg"
            visible.field.widget.attrs["placeholder"] = visible.field.label

    class Meta:
        widgets = {
            "address": forms.HiddenInput(),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }


class LostForm(BaseAddForm):
    """Form for creating an advertisement about a lost animal with hidden
    registration."""

    first_name = forms.CharField(
        label="Ваше имя",
        max_length=150,
        help_text="Ваше имя, будет видно в объявлениях и в личных сообщениях",
    )
    phone = PhoneNumberField(
        label="Номер мобильного телефона",
        help_text="Ваш номер телефона для связи",
        max_length=18,
    )
    email = forms.EmailField(
        label="Электронная почта",
        max_length=254,
        help_text="Будет использоваться для логина на сайте",
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox,
        label="Подтвердите что вы не робот",
        help_text="Подтвердите что вы не робот",
    )

    class Meta(BaseAddForm.Meta):
        model = Lost
        fields = (
            "address",
            "latitude",
            "longitude",
            "type",
            "image",
            "description",
            "pet_name",
            "age",
            "first_name",
            "phone",
            "email",
            "captcha",
        )


class FoundForm(LostForm):
    """Form for creating an advertisement about a found animal with hidden
    registration."""

    class Meta(LostForm.Meta):
        model = Found
        fields = (
            "address",
            "latitude",
            "longitude",
            "type",
            "image",
            "description",
            "age",
            "condition",
            "first_name",
            "phone",
            "email",
            "captcha",
        )


class AuthorizedLostForm(BaseAddForm):
    """Form for creating an advertisement about a lost animal."""

    class Meta(BaseAddForm.Meta):
        model = Lost
        fields = (
            "address",
            "latitude",
            "longitude",
            "type",
            "image",
            "description",
            "pet_name",
            "age",
        )


class AuthorizedFoundForm(BaseAddForm):
    """Form for creating an advertisement about a found animal."""

    class Meta(BaseAddForm.Meta):
        model = Found
        fields = (
            "address",
            "latitude",
            "longitude",
            "type",
            "image",
            "description",
            "age",
            "condition",
        )


class ProfileSettingsForm(forms.ModelForm):
    """Form for changing user settings in his profile."""

    class Meta:
        model = User
        fields = ("first_name", "contact_email", "contact_phone")


class SendMessageForm(forms.ModelForm):
    """Form for sending a message in a dialogue between two users."""

    class Meta:
        model = Message
        fields = ("content",)

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": ROWS_IN_DIALOG_MESSAGE_FORM,
                    "placeholder": "Введите сообщение",
                }
            )
        }
