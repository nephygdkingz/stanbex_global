from django import forms

from .models import Transaction


class DateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'


class TimeInput(forms.TimeInput):
    input_type = 'time'
    format = '%H:%M'


class BootstrapFormMixin:
    """Apply Bootstrap styling to all form fields."""
    def _apply_bootstrap_classes(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class TransactionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'account', 'amount', 'beneficiary_name', 'beneficiary_account',
            'beneficiary_bank', 'iban_number', 'description',
            'transaction_type', 'transaction_date', 'transaction_time', 'status',
        ]
        widgets = {
            'transaction_date': DateInput(),
            'transaction_time': TimeInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide the transaction type
        self.fields['transaction_type'].widget = forms.HiddenInput()

        # Apply Bootstrap styling
        self._apply_bootstrap_classes()

