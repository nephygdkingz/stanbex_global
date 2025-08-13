from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction


class CustomerTransactionCreateMixin(LoginRequiredMixin, CreateView):
    model = Transaction

    def dispatch(self, request, *args, **kwargs):
        if request.user.status == 'suspended':
            return HttpResponseRedirect(reverse_lazy('customer:suspended'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if hasattr(self.request.user, 'code'):
            return reverse_lazy('transaction:verify')

        status_url_map = {
            'Pending': 'transaction:pending',
            'Fail': 'transaction:failed',
            'Success': 'transaction:complete',
        }
        return reverse_lazy(
            status_url_map.get(self.request.user.transfer_status, 'customer:complete')
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['account'] = self.request.user.account
        return kwargs
