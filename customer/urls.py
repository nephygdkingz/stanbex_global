from django.urls import path

from . import views

app_name = 'customer'

urlpatterns = [
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path('statement/', views.userAccountStatement, name='account_statement'),
]