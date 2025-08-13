import math
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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


@login_required(login_url='account:login')
@check_suspended_user
def customer_dashboard(request):
    if request.user.status == 'suspended':
        return redirect('customer:suspended')

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
@check_suspended_user
def userAccountStatement(request):
    user_account = request.user.account
    all_transactions = Transaction.objects.filter(account=user_account)

    paginator = Paginator(all_transactions, 20)  

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'account': user_account
    }
    return render(request, 'customer/account_statement.html', context)


# transactions
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

        # Use atomic transaction to avoid partial saves
        with transaction.atomic():
            transfer = form.save(commit=False)

            # Populate hidden/required fields manually
            transfer.transaction_type = constants.DEBIT
            transfer.transaction_date = timezone.localtime().date()
            transfer.transaction_time = timezone.localtime().time()

            # Set account and balance
            transfer.account = account
            transfer.balance_after_transaction = account.balance

            # Determine status
            transfer.status = self._determine_status()
            transfer.save()

            if transfer.status in (constants.SUCCESSFUL, constants.PENDING):
                account.balance -= amount
                account.save(update_fields=['balance'])

            self.request.session['pk'] = transfer.pk

        # Send email notification
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
            'amount': transfer.amount,
            'date': timezone.localtime(),
            'currency': transfer.account.currency,
            'account_number': transfer.beneficiary_account,
            'summery': transfer.description,
            'balance': f'{transfer.account.currency}{transfer.balance_after_transaction}',
        }

        message = render_to_string(template, context)
        # try:
        #     email_send(subject, message, user.email)
        # except Exception as e:
        #     print(f"Email not sent: {e}")
