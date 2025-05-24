from functools import wraps
from django.shortcuts import redirect
from .models import Collaborator

def owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')

        is_owner = hasattr(user, 'owner_profile')  # Use lower-case relation
        is_collaborator = Collaborator.objects.filter(user=user).exists()

        if is_owner or is_collaborator:
            return view_func(request, *args, **kwargs)

        return redirect('/')  # or a permission-denied page
    return wrapper