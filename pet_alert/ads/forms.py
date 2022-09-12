from django import forms

from .models import Lost, Found


class LostForm(forms.ModelForm):
    class Meta:
        model = Lost
        fields = ('location', 'image', 'description', 'age', 'phone', 'email')


class FoundForm(forms.ModelForm):
    class Meta:
        model = Found
        fields = ('location', 'image', 'description',
                  'age', 'condition', 'phone', 'email')
