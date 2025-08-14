from django.urls import path

from . import views

app_name = 'customer'

urlpatterns = [
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path('statement/', views.userAccountStatement, name='account_statement'),
    path('loan/', views.loan, name='loan'),
    path('setting/', views.AccountSetting, name='account_setting'),
    path('change-password/', views.changePassword, name='change_password'),
    path('customer_care/', views.customer_care, name='customer_care'),
    path('suspended/', views.customerSuspended, name='suspended'),

    # transfer
    path("transafer_type/", views.select_transafer_type, name="transafer_type"),
    path("local-transfer/", views.LocalTransferView.as_view(), name="local_transfer"),
    path("international-transfer/", views.InternationalTransferView.as_view(), name="intern_transfer"),
    path('transaction/verify/', views.transactionVerify, name='verify'),
    path('transaction/completed/', views.transactionComplete, name='complete'),
    path('transaction/failed/', views.transactionFailed, name='failed'),
    path('transaction/pending/', views.transactionPending, name='pending'),
]