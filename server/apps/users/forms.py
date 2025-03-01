from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django_registration.forms import RegistrationForm

from server.apps.core.forms import CustomWidgetMixin

User = get_user_model()


class CreationForm(CustomWidgetMixin, RegistrationForm):
    """Custom registration form with form-control classes,
    placeholder and captcha."""

    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox, label="", help_text="Подтвердите что вы не робот"
    )

    class Meta(RegistrationForm.Meta):
        model = User
        fields = ("email", "first_name", "phone", "password1", "password2", "captcha")


class CreationFormWithoutPassword(RegistrationForm):
    """
    Registration form without password fields.
    Required for hidden registration during creating of advertisement for
    an unauthorized users.
    """

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
