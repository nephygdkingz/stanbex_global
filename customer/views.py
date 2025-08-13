from django.shortcuts import render

from .decorators import check_suspended_user
from .utils import get_client_ip

@check_suspended_user
def customer_dashboard(request):
    user = request.user.account
    ledger_balance = user.balance - 1500
    user_ip_address = get_client_ip(request)

    context = {
        'user': user,
        'ledger_balance': ledger_balance,
        'user_ip_address': user_ip_address,
    }
    return render(request, 'customer/dashboard.html', context)
