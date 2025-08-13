# myapp/decorators.py
from django.shortcuts import redirect
from functools import wraps

def check_suspended_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if getattr(request.user, 'status', None) == 'suspended':
                return redirect('customer:suspended')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
