"""
Author: Vlad Golub
"""

from django.http import JsonResponse
from .models import UserToken

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get('Authorization')
        if token:
            try:
                user = UserToken.objects.get(token=token)
                request.user = user
            except UserToken.DoesNotExist:
                return JsonResponse({'error': 'Invalid token'}, status=403)
        else:
            request.user = None
        return self.get_response(request)