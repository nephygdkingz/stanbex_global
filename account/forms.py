from django import forms
from django.forms import Select, SelectMultiple, CheckboxInput
from django.contrib.auth.forms import UserCreationForm

from .models import (MyUser, UserBankAccount)

class DateInput(forms.DateInput):
	input_type = 'date'
     

class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = MyUser
        fields = [
            'first_name', 'last_name', 'email', 'password1', 'password2',
            'gender', 'birth_date', 'title', 'password_text'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password_text'].widget = forms.HiddenInput()
        self.fields['birth_date'].widget = DateInput()

        for field in self.fields.values():
            if isinstance(field.widget, (Select, SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})



class UserBankAccountForm(forms.ModelForm):

    class Meta:
        model = UserBankAccount
        fields = ['street_address','city','postal_code','country',
                'account_type','currency',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field.widget, (Select, SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


