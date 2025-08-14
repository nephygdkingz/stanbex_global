from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls', namespace="frontend")),
    path('account/', include('account.urls', namespace="account")),
    path('account/customer/', include('customer.urls', namespace="customer")),
    path('account/transaction/', include('transaction.urls', namespace="transaction")),
    path('account/staff/', include('staff.urls', namespace="staff")),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
