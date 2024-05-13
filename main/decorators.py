# decorators.py

from functools import wraps
from .models import RequesAndResponseLog
from products.models import Cart
import json
from django.http import JsonResponse

def log_request(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        user_id = None
        if request.user.is_authenticated:
            user_id = request.user.id

        log_entry = RequesAndResponseLog.objects.create(
            user_id=user_id,
            request_path=request.path,
            request_data=json.dumps(request.POST) if request.method == 'POST' else json.dumps(request.GET)
        )

        response = view_func(request, *args, **kwargs)

        # Yanıt bilgilerini loglama
        log_entry.response_status_code = response.status_code
        if isinstance(response, JsonResponse):
            log_entry.response_data = json.dumps(response.json())
        else:
            log_entry.response_data = response.content.decode('utf-8')  

        log_entry.save()

        return response
    return wrapped_view


