from django.shortcuts import redirect
from .models import Customer
from django.contrib.auth.models import User
def anonymous_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('store')
        return view_func(request, *args, **kwargs)
    return wrapped_view
