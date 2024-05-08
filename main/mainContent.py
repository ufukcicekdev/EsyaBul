from customerauth.models import wishlist_model
from main.models import SocialMedia
from products.models import Cart, CartItem, Category


def mainContent(request):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent=None, is_active=True)
    wcount = 0
    hcount = 0
    cart_items = []
    cart_total = 0 

    session_key = request.session.session_key

    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
        except Cart.DoesNotExist:
            pass
        
        cart = Cart.objects.filter(user=request.user, order_completed=False).first()
        if cart:
            cart_items = cart.cartitem_set.all()

            for cart_item in cart_items:
                if cart_item.is_rental:
                    cart_total += cart_item.rental_price * cart_item.quantity
                else:
                    cart_total += cart_item.selling_price * cart_item.quantity
    else:
        try:
            temporary_cart = Cart.objects.get(session_key=session_key, order_completed=False)
            cart_items = temporary_cart.cartitem_set.all()
            for cart_item in cart_items:
                if cart_item.is_rental:
                    cart_total += cart_item.rental_price * cart_item.quantity
                else:
                    cart_total += cart_item.selling_price * cart_item.quantity

            try:
                handbag = Cart.objects.get(session_key=session_key, order_completed=False)
                hcount = CartItem.objects.filter(cart=handbag).count()
            except Cart.DoesNotExist:
                pass
        except Cart.DoesNotExist:
            pass

    context = {
        'social_media_links': social_media_links, 
        "wcount": wcount, 
        'main_categories': main_categories,
        "hcount": hcount,
        "main_categories2": main_categories,
        "main_categories4": main_categories,
        'cart_items': cart_items,
        'cart_total': cart_total, 
    }
        
    return context


