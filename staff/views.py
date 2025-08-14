from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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