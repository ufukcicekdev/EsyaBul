from customerauth.models import wishlist_model
from main.models import SocialMedia
from products.models import Cart, CartItem, Category
from django.core.cache import cache





def get_category():
    key = 'category'
    category = cache.get(key)
    if not category:
        category = list(Category.objects.filter(parent=None, is_active=True))
        cache.set(key, category, 60 * 60 * 6)  # 6 saat cache
    return category


def get_social_links():
    key = 'social_links'
    social_links = cache.get(key)
    if not social_links:
        social_links = SocialMedia.objects.all()
        cache.set(key, social_links, 60 * 60 * 6)  # 6 saat cache
    return social_links



def mainContent(request):
    social_media_links = get_social_links()
    main_categories = get_category()
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
            if session_key is not None:
                temporary_cart = Cart.objects.filter(session_key=session_key, order_completed=False).first()
                if temporary_cart:
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


