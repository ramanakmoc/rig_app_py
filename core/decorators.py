from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """
    Decorator to restrict views to specific roles.
    Usage:  @role_required('admin', 'supervisor')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                user_role = request.user.profile.role
            except Exception:
                messages.error(request, 'Access denied — no profile found.')
                return redirect('dashboard')
            if user_role not in roles:
                messages.error(request, f'Access denied. Requires role: {", ".join(roles)}.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    return role_required('admin')(view_func)


def supervisor_required(view_func):
    return role_required('admin', 'supervisor')(view_func)
