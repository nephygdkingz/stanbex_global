from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Sum, Count, Q
from django.db.models.functions import ExtractMonth, ExtractWeekDay
from datetime import datetime
import math

from .decorators import check_suspended_user
from .utils import get_client_ip
from transaction.models import Transaction

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
