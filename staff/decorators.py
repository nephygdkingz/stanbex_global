from functools import wraps
from django.shortcuts import redirect

def staff_required_redirect(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('customer:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
