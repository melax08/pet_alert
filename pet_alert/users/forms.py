from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django_registration.forms import RegistrationForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3, ReCaptchaV2Checkbox


User = get_user_model()


# class CreationForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = ('first_name', 'email', 'phone')

class CreationForm(RegistrationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox,
                             label='Подтвердите что вы не робот')

    class Meta(RegistrationForm.Meta):
        model = User
        fields = ('first_name', 'email', 'phone', 'captcha')


class CreationFormWithoutPassword(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    class Meta(RegistrationForm.Meta):
        model = User
        fields = ('first_name', 'email', 'phone')


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with form-control classes and placeholder."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'
            visible.field.widget.attrs['placeholder'] = visible.field.label
