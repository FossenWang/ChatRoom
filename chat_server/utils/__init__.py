import functools

from asgiref.sync import async_to_sync
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View


def async_to_sync_function(function):
    @functools.wraps(function)
    def sync_function(*args, **kwargs):
        return async_to_sync(function)(*args, **kwargs)
    return sync_function


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFView(View):
    def get(self, request):
        return JsonResponse({'csrftoken': request.META['CSRF_COOKIE']})
