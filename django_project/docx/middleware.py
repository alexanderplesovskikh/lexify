"""
Author: Vlad Golub
"""

'''
This file implements a Django middleware for token-based authentication. Key features:

1. Functionality:
   - Processes incoming requests to check for authentication tokens
   - Validates tokens against the UserToken model
   - Attaches authenticated user objects to requests

2. Implementation:
   - Custom middleware class following Django's middleware pattern
   - Checks 'Authorization' header for tokens
   - Returns 403 error for invalid tokens
   - Sets request.user to None for unauthenticated requests

3. Security:
   - Provides simple token authentication layer
   - Integrates with Django's request/response cycle
   - Rejects unauthorized access with JSON response

The middleware enables token-based authentication for Django views while handling both authenticated and unauthenticated requests.
'''

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