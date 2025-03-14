from django import forms

from .constants import ROWS_IN_DIALOG_MESSAGE_FORM
from .models import Message


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
