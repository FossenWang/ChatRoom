from django.http import JsonResponse, HttpRequest
from django.views import View
from django.contrib.auth import authenticate, login, logout


class LoginView(View):
    def post(self, request: HttpRequest):
        username = request.POST.get('username')
        password = request.POST.get('password')
        assert username and password, 'username and password are required'
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return JsonResponse({'login': False}, status=403)
        return JsonResponse({'login': True})


def logout_view(request):
    logout(request)
    return JsonResponse({'logout': True})


def user_view(request):
    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'avatar': user.avatar if user.is_authenticated else None,
    })
