from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django_registration.forms import RegistrationForm

User = get_user_model()


# class CreationForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = ('first_name', 'email', 'phone')

class CreationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User
        fields = ('first_name', 'email', 'phone')


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
