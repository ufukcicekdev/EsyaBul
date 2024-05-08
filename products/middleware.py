from django.utils.deprecation import MiddlewareMixin
from products.models import Cart

class MergeCartMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if 'temporary_session_key' in request.session:
                temporary_session_key = request.session['temporary_session_key']
                user_cart = Cart.objects.filter(user=request.user, order_completed=False).first()
                if user_cart is None and temporary_session_key:
                    try:
                        temporary_cart = Cart.objects.get(session_key=temporary_session_key, order_completed=False)
                        temporary_cart.session_key = None
                        temporary_cart.user = request.user
                        temporary_cart.save()
                    except Cart.DoesNotExist:
                        pass

