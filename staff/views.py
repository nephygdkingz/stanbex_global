from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import OperationalError

from .decorators import staff_required_redirect
from transaction.models import Transaction
from account.models import (MyUser, UserBankAccount, RequiredCode)
from .forms import UpdateUserAccountForm, UpdateUserBankAccountForm, RequiredCodeForm
from codes.models import OtpCode
from . import forms
from transaction import constants
from notification.email_utils import send_email_threaded, send_email_sync

@login_required(login_url='account:login')
@staff_required_redirect
def admin_dashboard(request):
    # Get the 10 most recent transactions
    recent_transactions = Transaction.objects.order_by('-transaction_date', '-transaction_time')[:10]
    
    # Count non-staff users
    customer_count = MyUser.objects.filter(is_staff=False).count()
    
    # All transactions and related metrics
    transactions = Transaction.objects.all()
    transaction_count = transactions.count()
    credit_count = transactions.filter(transaction_type='CR').count()
    debit_count = transactions.filter(transaction_type='DR').count()

    context = {
        'recent_transactions': recent_transactions,
        'customer_count': customer_count,
        'transaction_count': transaction_count,
        'credit_count': credit_count,
        'debit_count': debit_count,
    }

    return render(request, 'staff/dashboard.html', context)

@login_required(login_url='account:login')
@staff_required_redirect
def account_holders(request):
    # Get non-staff users ordered by creation date
    customers = MyUser.objects.filter(is_staff=False).order_by('-date_created')

    # Paginate the results, 20 per page
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/account_holders.html', {
        'account_holders': page_obj
    })

@login_required(login_url='account:login')
@staff_required_redirect
def all_transactions(request):
    transactions = Transaction.objects.all().order_by('-transaction_date', '-transaction_time')

    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/all_transactions.html', {
        'page_obj': page_obj
    })

@login_required(login_url='account:login')
@staff_required_redirect
def pending_transactions(request):
    transactions = Transaction.objects.filter(status='Pending').order_by('-transaction_date', '-transaction_time')

    return render(request, 'staff/pending_transactions.html', {
        'pending_transactions': transactions
    })


@login_required(login_url='account:login')
@staff_required_redirect
def update_user_account(request, pk):
    user = get_object_or_404(MyUser, id=pk)
    account_info = get_object_or_404(UserBankAccount, user=user)

    if request.method == 'POST':
        user_form = UpdateUserAccountForm(request.POST, instance=user)
        account_form = UpdateUserBankAccountForm(request.POST, instance=account_info)

        if user_form.is_valid() and account_form.is_valid():
            user_form.save()
            account_form.save()
            messages.success(request, 'Account was updated successfully.')
            return redirect('staff:account_holders')
    else:
        user_form = UpdateUserAccountForm(instance=user)
        account_form = UpdateUserBankAccountForm(instance=account_info)

    context = {
        'form': user_form,
        'acc_form': account_form
    }
    return render(request, 'staff/crud/update_account.html', context)


@login_required(login_url='account:login')
@staff_required_redirect
def delete_user_account(request, pk):
    user = get_object_or_404(MyUser, id=pk)

    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Account was deleted successfully.')
        return redirect('staff:account_holders')

    # Optional: render confirmation page before deletion
    # return render(request, 'account/admin/confirm_delete.html', {'user': user})

    # If not using confirmation, just redirect back
    messages.error(request, 'Invalid request method.')
    return redirect('staff:account_holders')


@login_required(login_url='account:login')
@staff_required_redirect
def add_required_code(request):
    if request.method == 'POST':
        form = RequiredCodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Code was added successfully')
            return redirect('staff:add_required_code')
    else:
        form = RequiredCodeForm()

    required_codes = RequiredCode.objects.all().order_by('-date_created')
    context = {
        'form': form,
        'required_code_customers': required_codes
    }
    return render(request, 'staff/required_code.html', context)

@login_required(login_url='account:login')
@staff_required_redirect
def delete_required_code(request, pk):
    try:
        code = RequiredCode.objects.get(id=pk)
        code.delete()
        messages.info(request, 'Code was deleted successfully')
    except RequiredCode.DoesNotExist:
        messages.warning(request, 'Code was already deleted or does not exist.')
    return redirect('staff:add_required_code')


@login_required(login_url='account:login')
@staff_required_redirect
def all_otp(request):
    context = {'all_otp': OtpCode.objects.all()}
    return render(request, 'staff/all_otp.html', context)


# transaction

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'staff/transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })

        return context
    

class DepositMoneyView(TransactionCreateMixin):
    form_class = forms.DepositForm
    title = 'Fund Customer Account'
    success_url = reverse_lazy('staff:deposit_money')

    def get_initial(self):
        return {
            'transaction_type': constants.CREDIT,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            data = kwargs.get('data').copy()
            data['transaction_type'] = constants.CREDIT
            kwargs['data'] = data
        return kwargs

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        customer_account = form.cleaned_data['account']

        try:
            account = UserBankAccount.objects.get(account_no=customer_account.account_no)
        except OperationalError as e:
            messages.error(self.request, 'There was a database error. Please try again later.')
            return self.form_invalid(form)

        transaction = form.save(commit=False)
        transaction.transaction_type = constants.CREDIT  # Ensure it's set
        transaction.balance_after_transaction = account.balance + amount
        transaction.save()

        account.balance += amount
        account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'{account.currency}{amount} has been successfully deposited to this account.'
        )

        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = forms.WithdrawForm
    title = 'Debit Customer Account'
    success_url = reverse_lazy('staff:withdraw_money')

    def get_initial(self):
        return {'transaction_type': constants.DEBIT}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            data = kwargs.get('data').copy()
            data['transaction_type'] = constants.DEBIT
            kwargs['data'] = data
        return kwargs

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        customer_account = form.cleaned_data['account']

        try:
            account = UserBankAccount.objects.get(account_no=customer_account.account_no)
        except OperationalError:
            messages.error(self.request, 'Database error occurred. Please try again later.')
            return self.form_invalid(form)

        if amount > account.balance:
            form.add_error('amount', 'Insufficient funds in this account.')
            return self.form_invalid(form)

        transaction = form.save(commit=False)
        transaction.transaction_type = constants.DEBIT  # Ensure it's set
        transaction.balance_after_transaction = account.balance - amount
        transaction.save()

        account.balance -= amount
        account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn {account.currency}{amount} from this account.'
        )

        return super().form_valid(form)
    
@login_required(login_url='account:login')
@staff_required_redirect
def approve_transaction(request, pk):
    transaction = get_object_or_404(Transaction, id=pk)

    transaction.status = "Successful"
    transaction.save()

    user = transaction.account.user
    email = user.email
    full_name = user.get_full_name()

    context = {
        'name': full_name,
        'amount': transaction.amount,
        'date': transaction.date_created,
        'currency': transaction.account.currency,
    }

    try:
        send_email_threaded(
            subject='Transaction Approved',
            to_email=email,
            context=context,
            html_template='emails/approved.html',
        )
    except Exception as e:
        # Use logging in production instead of print
        print(f"[Email Error] Failed to send approval email to {email}: {e}")

    messages.success(request, 'Transaction approved successfully.')
    return redirect('staff:pending_transactions')


@login_required(login_url='account:login')
@staff_required_redirect
def decline_transaction(request, pk):
    transaction = get_object_or_404(Transaction, id=pk)
    amount = transaction.amount
    account = transaction.account

    user_bank_account = get_object_or_404(UserBankAccount, account_no=account.account_no)
    user = user_bank_account.user

    # Update transaction
    transaction.status = "Failed"
    transaction.balance_after_transaction += amount
    transaction.save()

    # Update user bank account balance
    user_bank_account.balance = transaction.balance_after_transaction
    user_bank_account.save()

    # Prepare and send email
    template = 'emails/declined.html'
    context = {
        'name': user.get_full_name(),
        'amount': amount,
        'date': transaction.date_created,
        'currency': account.currency,
    }

    try:
        send_email_threaded(
            subject='Transaction Declined',
            to_email=user.email,
            context=context,
            html_template=template,
        )
    except Exception as e:
        # Use logging in production instead of print
        print(f"[Email Error] Failed to send approval email to {user.email}: {e}")

    messages.success(request, 'Transaction was declined successfully.')
    return redirect('staff:pending_transactions')
