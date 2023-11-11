from django import forms


class CustomWidgetMixin(forms.Form):
    """Custom form mixin with form-control classes
    and placeholder with label information."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs[
                'class'] = 'form-control form-control-lg'
            visible.field.widget.attrs['placeholder'] = visible.field.label
