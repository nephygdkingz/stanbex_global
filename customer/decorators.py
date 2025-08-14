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


def check_not_suspended_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            # If the user is NOT suspended, allow access
            if getattr(request.user, 'status', None) != 'suspended':
                return view_func(request, *args, **kwargs)
            # If suspended, redirect them
            return redirect('customer:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# def check_user_suspension(require_suspended=True):
#     """
#     Decorator to restrict access based on user suspension status.
    
#     - If require_suspended=True: only allow suspended users.
#     - If require_suspended=False: only allow NON-suspended users.
#     """
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, *args, **kwargs):
#             if request.user.is_authenticated:
#                 user_status = getattr(request.user, 'status', None)
                
#                 if require_suspended and user_status != 'suspended':
#                     # Block non-suspended users
#                     return redirect('customer:dashboard')  # or any other appropriate page
#                 elif not require_suspended and user_status == 'suspended':
#                     # Block suspended users
#                     return redirect('customer:suspended')
                    
#             return view_func(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator
