from django import forms

from .models import Lost, Found


class LostForm(forms.ModelForm):
    class Meta:
        model = Lost
        fields = ('location', 'image', 'description', 'pet_name',
                  'age', 'name', 'phone', 'email')


class FoundForm(forms.ModelForm):
    class Meta:
        model = Found
        fields = ('location', 'image', 'description',
                  'age', 'name', 'condition', 'phone', 'email')
