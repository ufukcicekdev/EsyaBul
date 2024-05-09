from django.utils.deprecation import MiddlewareMixin
from products.models import Cart

from django.db import transaction

class MergeCartMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if 'temporary_session_key' in request.session:
                temporary_session_key = request.session['temporary_session_key']
                try:
                    temporary_cart = Cart.objects.get(session_key=temporary_session_key, order_completed=False)
                    with transaction.atomic():
                        user_cart = Cart.objects.select_for_update().filter(user=request.user, order_completed=False).first()
                        if user_cart:
                            for item in temporary_cart.items.all():
                                item.cart = user_cart
                                item.save()
                            temporary_cart.delete()  
                        else:
                            temporary_cart.session_key = None
                            temporary_cart.user = request.user
                            temporary_cart.save()
                except Cart.DoesNotExist:
                    pass

