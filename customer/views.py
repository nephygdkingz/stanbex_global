import math
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.db.models import Avg, Sum, Count, Q
from django.db.models.functions import ExtractMonth, ExtractWeekDay
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.template.loader import render_to_string
from django.db import transaction

from . import forms
from .decorators import check_suspended_user
from .utils import get_client_ip
from transaction.models import Transaction
from transaction.mixins import CustomerTransactionCreateMixin
from transaction import constants
from notification.email_utils import send_email_threaded, send_email_sync


@login_required(login_url='account:login')
@check_suspended_user
def customer_dashboard(request):
    user = request.user.account
    ledger_balance = user.balance - 1500

    # Transactions for this account
    all_transactions = Transaction.objects.filter(account=user)

    # Aggregate counts and sums in one query
    aggregates = all_transactions.aggregate(
        all_sum=Sum('amount'),
        credit_sum=Sum('amount', filter=Q(transaction_type='CR')),
        debit_sum=Sum('amount', filter=Q(transaction_type='DR')),
        credit_count=Count('id', filter=Q(transaction_type='CR')),
        debit_count=Count('id', filter=Q(transaction_type='DR')),
        all_count=Count('id')
    )

    # Helper function to safely calculate percentages
    def percent(part, total, round_fn):
        part = part or 0
        total = total or 0
        return round_fn((part * 100) / total) if total else 0

    # Percentages
    debit_percent = percent(aggregates["debit_count"], aggregates["all_count"], math.ceil)
    credit_percent = percent(aggregates["credit_count"], aggregates["all_count"], math.floor)
    gross_credit_percent = percent(aggregates["credit_sum"], aggregates["all_sum"], math.ceil)
    gross_debit_percent = percent(aggregates["debit_sum"], aggregates["all_sum"], math.floor)

    # Chart data: average balance after transaction per month
    graph_trans = (
        all_transactions
        .annotate(month=ExtractMonth("transaction_date"))
        .values("month")
        .annotate(sum=Avg("balance_after_transaction"))
        .order_by("month")
    )
    month_of_year = [
        datetime.strptime(str(item['month']), '%m').strftime('%B')
        for item in graph_trans
    ]
    total_transaction = [item['sum'] or 0 for item in graph_trans]

    # Withdrawals per weekday (Mon-Sat)
    withdrawals_per_day = (
        all_transactions
        .filter(transaction_type='DR')
        .annotate(weekday=ExtractWeekDay('transaction_date'))
        .values('weekday')
        .annotate(total=Count('id'))
    )
    weekday_map = {1: 'Sun', 2: 'Mon', 3: 'Tue', 4: 'Wed', 5: 'Thu', 6: 'Fri', 7: 'Sat'}

    withdrawals_labels = []
    withdrawals_data = []
    for i in range(2, 8):  # Monday (2) → Saturday (7)
        withdrawals_labels.append(weekday_map[i])
        count = next((x['total'] for x in withdrawals_per_day if x['weekday'] == i), 0)
        withdrawals_data.append(count)

    # Context for template
    context = {
        'credit_count': aggregates["credit_count"] or 0,
        'debit_count': aggregates["debit_count"] or 0,
        'credit_percent': credit_percent,
        'debit_percent': debit_percent,
        'gross_debit_percent': gross_debit_percent,
        'gross_credit_percent': gross_credit_percent,
        'ledger_balance': ledger_balance,
        'month': month_of_year,
        'sum': total_transaction,
        'user_ip_address': get_client_ip(request),
        'all_debit': aggregates["debit_sum"] or 0,
        'withdrawals_labels': withdrawals_labels,
        'withdrawals_data': withdrawals_data
    }

    return render(request, 'customer/dashboard.html', context)


@login_required(login_url='account:login')
def customerSuspended(request):
    user = request.user.account
    ledger_balance = user.balance - 1500

    # Transactions for this account
    all_transactions = Transaction.objects.filter(account=user)

    # Aggregate counts and sums in one query
    aggregates = all_transactions.aggregate(
        all_sum=Sum('amount'),
        credit_sum=Sum('amount', filter=Q(transaction_type='CR')),
        debit_sum=Sum('amount', filter=Q(transaction_type='DR')),
        credit_count=Count('id', filter=Q(transaction_type='CR')),
        debit_count=Count('id', filter=Q(transaction_type='DR')),
        all_count=Count('id')
    )

    # Helper function to safely calculate percentages
    def percent(part, total, round_fn):
        part = part or 0
        total = total or 0
        return round_fn((part * 100) / total) if total else 0
    
    # Percentages
    debit_percent = percent(aggregates["debit_count"], aggregates["all_count"], math.ceil)
    credit_percent = percent(aggregates["credit_count"], aggregates["all_count"], math.floor)
    gross_credit_percent = percent(aggregates["credit_sum"], aggregates["all_sum"], math.ceil)
    gross_debit_percent = percent(aggregates["debit_sum"], aggregates["all_sum"], math.floor)

    # Chart data: average balance after transaction per month
    graph_trans = (
        all_transactions
        .annotate(month=ExtractMonth("transaction_date"))
        .values("month")
        .annotate(sum=Avg("balance_after_transaction"))
        .order_by("month")
    )
    month_of_year = [
        datetime.strptime(str(item['month']), '%m').strftime('%B')
        for item in graph_trans
    ]
    total_transaction = [item['sum'] or 0 for item in graph_trans]

    # Withdrawals per weekday (Mon-Sat)
    withdrawals_per_day = (
        all_transactions
        .filter(transaction_type='DR')
        .annotate(weekday=ExtractWeekDay('transaction_date'))
        .values('weekday')
        .annotate(total=Count('id'))
    )
    weekday_map = {1: 'Sun', 2: 'Mon', 3: 'Tue', 4: 'Wed', 5: 'Thu', 6: 'Fri', 7: 'Sat'}

    withdrawals_labels = []
    withdrawals_data = []
    for i in range(2, 8):  # Monday (2) → Saturday (7)
        withdrawals_labels.append(weekday_map[i])
        count = next((x['total'] for x in withdrawals_per_day if x['weekday'] == i), 0)
        withdrawals_data.append(count)

    # Context for template
    context = {
        'credit_count': aggregates["credit_count"] or 0,
        'debit_count': aggregates["debit_count"] or 0,
        'credit_percent': credit_percent,
        'debit_percent': debit_percent,
        'gross_debit_percent': gross_debit_percent,
        'gross_credit_percent': gross_credit_percent,
        'ledger_balance': ledger_balance,
        'month': month_of_year,
        'sum': total_transaction,
        'user_ip_address': get_client_ip(request),
        'all_debit': aggregates["debit_sum"] or 0,
        'withdrawals_labels': withdrawals_labels,
        'withdrawals_data': withdrawals_data
    }

    return render(request, 'customer/suspended.html', context)

@login_required(login_url='account:login')
@check_suspended_user
def userAccountStatement(request):
    user_account = request.user.account
    all_transactions = Transaction.objects.filter(account=user_account)

    paginator = Paginator(all_transactions, 20)  

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'account': user_account,
        'user_ip_address': get_client_ip(request),
    }
    return render(request, 'customer/account_statement.html', context)

@login_required(login_url='account:login')
@check_suspended_user
def loan(request):
    context = {'user_ip_address': get_client_ip(request)}
    return render(request, 'customer/loan.html', context)


@login_required(login_url='account:login')
@check_suspended_user
def AccountSetting(request):
    user = request.user
    user_form = forms.UpdateCustomerAccountForm(instance=user)
    if request.method == 'POST':
        user_form = forms.UpdateCustomerAccountForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            
            messages.info(request, 'Your account was updated successfully!')
            return redirect('customer:account_setting')

    context = {
        'form':user_form,
        'user_ip_address': get_client_ip(request),
        }
    return render(request, 'customer/setting.html', context)


@login_required(login_url='account:login')
@check_suspended_user
def changePassword(request):
    if request.method == 'POST':
        form = forms.SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            
            user.password_text = form.cleaned_data['new_password1']
            user.save(update_fields=['password_text'])

            # Keep the user logged in
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was changed successfully!')
            return redirect('customer:change_password')
    else:
        form = forms.SetPasswordForm(request.user)

    return render(request, 'customer/change_password.html', {'form': form})


@login_required(login_url='account:login')
def customer_care(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        final_message = 'emails/customer_care_email.html' 
        context = {
            'name': name,
            'email': email,
            'message': message,
            'subject': subject
        }
        try:
            send_email_sync(
                subject=subject,
                to_email='support@stanbexglobalonline.com',
                # to_email='support@stanbexglobalonline.com',
                html_template=final_message,
                context=context,
            )
            messages.success(request, 'Email sent successfully, we will get back to you as soon as possible')
        except:
            messages.error(request, 'There was an error while trying to send your email, please try again')

        finally:
            return redirect('customer:customer_care')
    return render(request, 'customer/customer_care.html')


# transactions
@login_required(login_url='base:home')
def select_transafer_type(request):
    if request.method == 'POST':
        selected_location = request.POST.get('location')

        if selected_location == 'local':
            return redirect('customer:local_transfer')
        elif selected_location == 'international':
            return redirect('customer:intern_transfer')

        return redirect('account:customer_dashboard')


class LocalTransferView(CustomerTransactionCreateMixin):
    form_class = forms.CustomerTransactionForm
    template_name = 'customer/transactions/local_transfer.html'

    def get_initial(self):
        now = timezone.localtime()
        return {
            'transaction_type': constants.DEBIT,
            'transaction_date': now.date(),
            'transaction_time': now.time(),
        }

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        account = self.request.user.account

        with transaction.atomic():
            transfer = form.save(commit=False)

            # Populate hidden/required fields
            transfer.transaction_type = constants.DEBIT
            transfer.transaction_date = timezone.localtime().date()
            transfer.transaction_time = timezone.localtime().time()
            transfer.account = account
            transfer.balance_after_transaction = account.balance

            transfer.status = self._determine_status()
            transfer.save()

            if not hasattr(self.request.user, 'code'):
                if transfer.status in (constants.SUCCESSFUL, constants.PENDING):
                    account.balance -= amount
                    account.save(update_fields=['balance'])
                    transfer.balance_after_transaction = account.balance
                    transfer.save(update_fields=['balance_after_transaction'])

            self.request.session['pk'] = transfer.pk

        # Only send email if user has NO code
        if not hasattr(self.request.user, 'code'):
            self._send_transaction_email(transfer)

        return super().form_valid(form)

    def _determine_status(self):
        status_map = {
            'Pending': constants.PENDING,
            'Fail': constants.FAILED,
        }
        return status_map.get(self.request.user.transfer_status, constants.SUCCESSFUL)

    def _send_transaction_email(self, transfer):
        user = self.request.user
        templates = {
            constants.PENDING: 'emails/transaction_pending_email.html',
            constants.FAILED: 'emails/transaction_failed_email.html',
            constants.SUCCESSFUL: 'emails/transaction_complete_email.html',
        }
        subjects = {
            constants.PENDING: 'Transaction Pending',
            constants.FAILED: 'Transaction Failed',
            constants.SUCCESSFUL: 'Transaction Completed',
        }

        template = templates.get(transfer.status)
        subject = subjects.get(transfer.status)

        if not template or not subject:
            return

        context = {
            'name': user.get_full_name(),
            'amount': f'{transfer.account.currency}{transfer.amount:.2f}',
            'date': timezone.localtime(),
            'currency': transfer.account.currency,
            'account_number': transfer.beneficiary_account,
            'summery': transfer.description,
            'balance': f'{transfer.account.currency}{transfer.account.balance:.2f}',
        }

        try:
            send_email_threaded(
                subject=subject,
                to_email=user.email,
                context=context,
                html_template=template
            )
        except Exception as e:
            print(f"Email not sent: {e}")


class InternationalTransferView(CustomerTransactionCreateMixin):
    form_class = forms.CustomerTransactionForm
    template_name = 'customer/transactions/international_transfer.html'

    def get_initial(self):
        now = timezone.localtime()
        return {
            'transaction_type': constants.DEBIT,
            'transaction_date': now.date(),
            'transaction_time': now.time(),
        }

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        account = self.request.user.account

        with transaction.atomic():
            transfer = form.save(commit=False)

            # Populate hidden/required fields
            transfer.transaction_type = constants.DEBIT
            transfer.transaction_date = timezone.localtime().date()
            transfer.transaction_time = timezone.localtime().time()
            transfer.account = account
            transfer.balance_after_transaction = account.balance

            transfer.status = self._determine_status()
            transfer.save()

            if not hasattr(self.request.user, 'code'):
                if transfer.status in (constants.SUCCESSFUL, constants.PENDING):
                    account.balance -= amount
                    account.save(update_fields=['balance'])
                    transfer.balance_after_transaction = account.balance
                    transfer.save(update_fields=['balance_after_transaction'])

            self.request.session['pk'] = transfer.pk

        # Only send email if user has NO code
        if not hasattr(self.request.user, 'code'):
            self._send_transaction_email(transfer)

        return super().form_valid(form)

    def _determine_status(self):
        status_map = {
            'Pending': constants.PENDING,
            'Fail': constants.FAILED,
        }
        return status_map.get(self.request.user.transfer_status, constants.SUCCESSFUL)

    def _send_transaction_email(self, transfer):
        user = self.request.user
        templates = {
            constants.PENDING: 'emails/transaction_pending_email.html',
            constants.FAILED: 'emails/transaction_failed_email.html',
            constants.SUCCESSFUL: 'emails/transaction_complete_email.html',
        }
        subjects = {
            constants.PENDING: 'Transaction Pending',
            constants.FAILED: 'Transaction Failed',
            constants.SUCCESSFUL: 'Transaction Completed',
        }

        template = templates.get(transfer.status)
        subject = subjects.get(transfer.status)

        if not template or not subject:
            return

        context = {
            'name': user.get_full_name(),
            'amount': f'{transfer.account.currency}{transfer.amount:.2f}',
            'date': timezone.localtime(),
            'currency': transfer.account.currency,
            'account_number': transfer.beneficiary_account,
            'summery': transfer.description,
            'balance': f'{transfer.account.currency}{transfer.account.balance:.2f}',
        }

        try:
            send_email_threaded(
                subject=subject,
                to_email=user.email,
                context=context,
                html_template=template
            )
        except Exception as e:
            print(f"Email not sent: {e}")


@login_required(login_url='account:login')
@check_suspended_user
def transactionVerify(request):
    user = request.user

    required_code = user.code
    user_account = user.account
    pk = request.session.get('pk')

    if not pk:
        messages.error(request, "No transaction found in session.")
        return redirect('customer:customer_dashboard')

    transaction = Transaction.objects.filter(account=user_account, pk=pk).first()
    if not transaction:
        messages.error(request, "Transaction not found or invalid.")
        return redirect('customer:customer_dashboard')

    if request.method == 'POST':
        transaction_code = request.POST.get('trans-code')

        if transaction_code != required_code.code_number:
            transaction.status = 'Failed'
            transaction.save()
            messages.error(request, "Incorrect code, please try again.")
            return redirect('customer:verify')

        # Determine status
        if user.transfer_status == 'Pending':
            transaction.status = 'Pending'
        elif user.transfer_status == 'Fail':
            transaction.status = 'Failed'
        else:
            transaction.status = 'Successful'

        # Update balances only if transaction is Pending or Successful
        if transaction.status in ('Pending', 'Successful'):
            transaction.balance_after_transaction = user_account.balance - transaction.amount
            user_account.balance = transaction.balance_after_transaction
            user_account.save(update_fields=['balance'])

        transaction.save()

        # Send email
        email_templates = {
            'Pending': 'emails/transaction_pending_email.html',
            'Failed': 'emails/transaction_failed_email.html',
            'Successful': 'emails/transaction_complete_email.html',
        }

        email_subjects = {
            'Pending': 'Transaction Pending',
            'Failed': 'Transaction Failed',
            'Successful': 'Transaction Completed',
        }

        context = {
            'name': f'{user.first_name} {user.last_name}',
            'amount': f'{transaction.account.currency}{transaction.amount}',
            'date': timezone.localtime(),
            'currency': transaction.account.currency,
            'account_number': str(transaction.beneficiary_account),
            'summery': transaction.description,
            'balance': f'{transaction.account.currency}{transaction.account.balance:.2f}',
        }

        try:
            send_email_threaded(
                subject=email_subjects[transaction.status],
                to_email=user.email,
                context=context,
                html_template=email_templates[transaction.status]
            )
        except Exception as e:
            print(f"Email not sent: {e}")

        # Save the transaction PK in session for "complete" page
        request.session['pk'] = transaction.pk

        # Redirect based on status
        redirect_map = {
            'Pending': 'customer:pending',
            'Failed': 'customer:failed',
            'Successful': 'customer:complete',
        }
        return redirect(redirect_map[transaction.status])

    return render(request, 'customer/transactions/verify.html', {'required_code': required_code})


@login_required(login_url='account:login')
@check_suspended_user
def transactionComplete(request):
    pk = request.session.get('pk')
    if not pk:
        messages.error(request, "No transaction to display.")
        return redirect('customer:local_transfer')  # e.g., dashboard

    current_transaction = Transaction.objects.filter(
        account=request.user.account, pk=pk
    ).first()

    if not current_transaction:
        messages.error(request, "Transaction not found.")
        return redirect('customer:local_transfer')

    context = {'transaction': current_transaction}
    return render(request, 'customer/transactions/complete.html', context)


@login_required(login_url='account:login')
@check_suspended_user
def transactionFailed(request):
    return render(request, 'customer/transactions/Failed.html')


@login_required(login_url='account:login')
@check_suspended_user
def transactionPending(request):
    return render(request, 'customer/transactions/pending.html')