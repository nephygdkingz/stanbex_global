from decimal import Decimal
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm

from transaction.models import Transaction
from transaction.forms import DateInput, TimeInput, BootstrapFormMixin
User = get_user_model()

class CustomerTransactionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount', 'beneficiary_name', 'beneficiary_account',
            'beneficiary_bank', 'iban_number', 'description', 'route_code',
            'transaction_type', 'transaction_date', 'transaction_time',
            'beneficiary_address', 'bank_address',
        ]
        widgets = {
            'transaction_date': DateInput(),
            'transaction_time': TimeInput(),
            'transaction_type': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        # Hidden fields should not be required in the form
        self.fields['transaction_type'].required = False
        self.fields['transaction_date'].required = False
        self.fields['transaction_time'].required = False

        # Apply Bootstrap classes
        self._apply_bootstrap_classes()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save(commit=commit)

    def clean_amount(self):
        account = self.account
        min_amount = Decimal(account.account_type.minimum_withdraw)
        max_amount = Decimal(account.account_type.maximum_withdraw)
        balance = Decimal(account.balance)

        amount = self.cleaned_data.get('amount')
        if amount is None:
            return amount

        if amount < min_amount:
            raise forms.ValidationError(
                f"You cannot transfer less than {account.currency}{min_amount}"
            )
        if amount > max_amount:
            raise forms.ValidationError(
                f"You cannot transfer more than {account.currency}{max_amount}"
            )
        if amount > balance:
            raise forms.ValidationError(
                f"You have {balance} {account.currency}. You cannot transfer more than your balance."
            )
        return amount
    

class UpdateCustomerAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'birth_date', 'title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Birth date with HTML5 date picker
        self.fields['birth_date'].widget = DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })

        # Add Bootstrap class to all other fields
        for name, field in self.fields.items():
            if name != 'birth_date':
                field.widget.attrs.update({'class': 'form-control'})


class SetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control mb-3'})
