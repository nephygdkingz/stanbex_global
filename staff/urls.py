from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('account-holders/', views.account_holders, name='account_holders'),
    path('transaction-list/', views.all_transactions, name='all_transactions'),
    path('pending-transactions/', views.pending_transactions, name='pending_transactions'),
    path('add-required-code/', views.add_required_code, name='add_required_code'),
    path('otp-list/', views.all_otp, name='all_otp'),
    path('password-update-list/', views.admin_update_passwords_view, name='password_update_list'),
    path('update_user_password/<int:pk>/', views.admin_change_user_password, name='admin_change_user_password'),

    # crud operations
    path('update_user/<str:pk>/', views.update_user_account, name='update_user'),
    path('delete_user/<str:pk>/', views.delete_user_account, name='delete_user'),
    path('delete-required-code/<str:pk>/', views.delete_required_code, name='delete_code'),

    # transaction operations
    path("deposit/", views.DepositMoneyView.as_view(), name="deposit_money"),
    path("withdraw/", views.WithdrawMoneyView.as_view(), name="withdraw_money"),
    path('approve/<str:pk>/', views.approve_transaction, name='approve'),
    path('decline/<str:pk>/', views.decline_transaction, name='decline'),
    path('delete_transaction/<str:pk>/', views.delete_transaction, name='delete_trans'),
]