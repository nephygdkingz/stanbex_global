from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Sum, Count, Q
from django.db.models.functions import ExtractMonth
from datetime import datetime
import math

from .decorators import check_suspended_user
from .utils import get_client_ip
from transaction.models import Transaction


@check_suspended_user
def customer_dashboard(request):
    user = request.user.account
    ledger_balance = user.balance - 1500
    user_ip_address = get_client_ip(request)

    # Base queryset
    all_transactions = Transaction.objects.filter(account=user)

    # Precompute aggregates in fewer queries
    aggregates = all_transactions.aggregate(
        all_sum=Sum('amount'),
        all_count=Count('id'),
        credit_sum=Sum('amount', filter=Q(transaction_type='CR')),
        credit_count=Count('id', filter=Q(transaction_type='CR')),
        debit_sum=Sum('amount', filter=Q(transaction_type='DR')),
        debit_count=Count('id', filter=Q(transaction_type='DR'))
    )

    # Monthly graph data
    graph_data = (
        all_transactions
        .annotate(month=ExtractMonth("transaction_date"))
        .values("month")
        .annotate(sum=Avg("balance_after_transaction"))
        .order_by("month")
    )

    month_of_year = [
        datetime.strptime(str(row["month"]), "%m").strftime("%B")
        for row in graph_data
    ]
    total_transaction = [row["sum"] for row in graph_data]

    # Avoid ZeroDivisionError with safe division
    def percent(part, total, round_fn):
        part = part or 0
        total = total or 0
        return round_fn((part * 100) / total) if total else 0

    debit_percent = percent(aggregates["debit_count"], aggregates["all_count"], math.ceil)
    credit_percent = percent(aggregates["credit_count"], aggregates["all_count"], math.floor)
    gross_credit_percent = percent(aggregates["credit_sum"], aggregates["all_sum"], math.ceil)
    gross_debit_percent = percent(aggregates["debit_sum"], aggregates["all_sum"], math.floor)


    context = {
        'credit_count': aggregates["credit_count"],
        'debit_count': aggregates["debit_count"],
        'credit_percent': credit_percent,
        'debit_percent': debit_percent,
        'gross_debit_percent': gross_debit_percent,
        'gross_credit_percent': gross_credit_percent,
        'user': user,
        'ledger_balance': ledger_balance,
        'month': month_of_year,
        'sum': total_transaction,
        'user_ip_address': user_ip_address,
        'all_debit': aggregates["debit_sum"] or 0
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

    context = {'page_obj':page_obj}
    return render(request, 'customer/account_statement.html', context)
