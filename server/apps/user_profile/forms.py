from django import forms

from server.apps.users.models import User


class ProfileSettingsForm(forms.ModelForm):
    """Form for changing user settings in his profile."""

    class Meta:
        model = User
        fields = ("first_name", "contact_email", "contact_phone")
