from django import forms
from account.models import UserBankAccount , MyUser, RequiredCode
from django.forms import DateInput


class UpdateUserAccountForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'gender',
            'birth_date',
            'title',
            'password_text',
            'status',
            'transfer_status',
            'otp_status',
            'created_on',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use a date input widget for date fields
        date_fields = ['birth_date', 'created_on']
        for field in date_fields:
            self.fields[field].widget = DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })

        # Add 'form-control' class to all other fields
        for name, field in self.fields.items():
            if name not in date_fields:
                field.widget.attrs['class'] = 'form-control'


class UpdateUserBankAccountForm(forms.ModelForm):
    class Meta:
        model = UserBankAccount
        fields = [
            'country',
            'account_type',
            'currency',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class RequiredCodeForm(forms.ModelForm):
    class Meta:
        model = RequiredCode
        fields = ['user', 'code_name', 'code_number']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'code_name': forms.TextInput(attrs={'class': 'form-control'}),
            'code_number': forms.TextInput(attrs={'class': 'form-control'}),
        }