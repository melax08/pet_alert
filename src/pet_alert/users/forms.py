from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from core.forms import CustomWidgetMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django_registration.forms import RegistrationForm

User = get_user_model()


class CreationForm(CustomWidgetMixin, RegistrationForm):
    """Custom registration from with form-control classes,
    placeholder and captcha."""

    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox, label="", help_text="Подтвердите что вы не робот"
    )

    class Meta(RegistrationForm.Meta):
        model = User
        fields = ("email", "first_name", "phone", "password1", "password2", "captcha")


class CreationFormWithoutPassword(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password2"].required = False
        self.fields["password1"].widget.attrs["autocomplete"] = "off"
        self.fields["password2"].widget.attrs["autocomplete"] = "off"

    class Meta(RegistrationForm.Meta):
        model = User
        fields = ("first_name", "email", "phone")


class CustomAuthenticationForm(CustomWidgetMixin, AuthenticationForm):
    """Custom login form with form-control classes and placeholder."""

    pass


class CustomResetForm(CustomWidgetMixin, PasswordResetForm):
    """Custom reset from with form-control classes, placeholder and captcha."""

    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox, label="", help_text="Подтвердите что вы не робот"
    )


class CustomPasswordChangeForm(CustomWidgetMixin, PasswordChangeForm):
    """Custom password change form
    with form-control classes and placeholder."""

    pass


class CustomSetPasswordForm(CustomWidgetMixin, SetPasswordForm):
    """Custom password set form with form-control classes and placeholder."""

    pass
