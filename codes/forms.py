from django import forms

from .models import OtpCode

class CodeForm(forms.ModelForm):
    number = forms.CharField(
        label='',  
        help_text='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter OTP code',  # Placeholder instead of label
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = OtpCode
        fields = ['number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If you want all form fields to have the same styling
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')