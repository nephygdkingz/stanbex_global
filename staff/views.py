from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .decorators import staff_required_redirect
from transaction.models import Transaction
from account.models import (MyUser, UserBankAccount, RequiredCode)

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