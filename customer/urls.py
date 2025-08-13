from django.urls import path

from . import views

app_name = 'customer'

urlpatterns = [
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path('statement/', views.userAccountStatement, name='account_statement'),

    # transfer
    path("account/local-transfer/", views.LocalTransferView.as_view(), name="local_transfer"),
]