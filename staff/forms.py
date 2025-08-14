from django import forms
from account.models import UserBankAccount , MyUser, RequiredCode
from django.forms import DateInput

from transaction.forms import TransactionForm

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


class DepositForm(TransactionForm):
    min_deposit_amount = 100  # class attribute for easier override

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            return amount  # Let the field-level validators handle this

        # Get currency safely; fallback to empty string if missing
        account = self.cleaned_data.get('account')
        currency = getattr(account, 'currency', '') if account else ''

        if amount < self.min_deposit_amount:
            raise forms.ValidationError(
                f'You cannot deposit less than {self.min_deposit_amount}{currency}'
            )
        return amount


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        account_obj = self.cleaned_data.get('account')

        if not amount or not account_obj:
            # Let the base form validators handle required field errors
            return amount

        try:
            account = UserBankAccount.objects.get(account_no=account_obj.account_no)
        except UserBankAccount.DoesNotExist:
            raise forms.ValidationError("Invalid account provided.")

        min_withdraw = account.account_type.minimum_withdraw
        max_withdraw = account.account_type.maximum_withdraw
        balance = account.balance
        currency = account.currency

        if amount < min_withdraw:
            raise forms.ValidationError(
                f"You cannot withdraw less than {currency}{min_withdraw}"
            )

        if amount > max_withdraw:
            raise forms.ValidationError(
                f"You cannot withdraw more than {currency}{max_withdraw}"
            )

        if amount > balance:
            raise forms.ValidationError(
                f"You have {balance} {currency} in this account. "
                f"You cannot withdraw more than the available balance."
            )

        return amount
