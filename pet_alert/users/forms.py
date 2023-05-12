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
