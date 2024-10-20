from functools import wraps
from django.shortcuts import HttpResponse
def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse("401 - Unauthorized (You have to login to access this page.)")
    return wrapper