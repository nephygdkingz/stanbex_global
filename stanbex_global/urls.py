from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls', namespace="frontend")),
    path('account/', include('account.urls', namespace="account")),
    path('account/customer/', include('customer.urls', namespace="customer")),
    path('account/transaction/', include('transaction.urls', namespace="transaction")),
]
