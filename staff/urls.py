from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('account-holders/', views.account_holders, name='account_holders'),
    path('transaction-list/', views.all_transactions, name='all_transactions'),
]