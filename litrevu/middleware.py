from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """Redirige les visiteurs non connectés vers la connexion."""

    def __init__(self, get_response):
        self.get_response = get_response
        prefix = settings.STATIC_URL.lstrip('/')
        self.public_prefixes = (
            reverse('login'),
            reverse('signup'),
            '/admin/',
            f'/{prefix}',
            '/media/',
        )

    def __call__(self, request):
        if (
            not request.user.is_authenticated
            and not self._is_public(request.path)
        ):
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)

    def _is_public(self, path):
        return any(path.startswith(prefix) for prefix in self.public_prefixes)
