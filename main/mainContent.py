from customerauth.models import wishlist_model
from main.models import SocialMedia
from products.models import Cart, CartItem, Category
from django.core.cache import cache
from django.template.loader import render_to_string




def get_category():
    key = 'main_categories_html'
    main_categories_html = cache.get(key)
    
    if not main_categories_html:
        main_categories = Category.objects.filter(parent=None, is_active=True).prefetch_related('children')
        
        main_categories_html = ""
        for category in main_categories:
            category_html = render_to_string('coreBase/category_block.html', {'category': category})
            main_categories_html += category_html

        cache.set(key, main_categories_html, 60 * 60 * 6)  
        
    return main_categories_html

def get_social_links():
    key = 'social_links'
    social_links = cache.get(key)
    if not social_links:
        social_links = SocialMedia.objects.all()
        cache.set(key, social_links, 60 * 60 * 6)  # 6 saat cache
    return social_links



def get_footer_category():
    key = 'category'
    category = cache.get(key)
    if not category:
        category = list(Category.objects.filter(parent=None, is_active=True))
        cache.set(key, category, 60 * 60 * 6)  # 6 saat cache
    return category




def mainContent(request):
    main_categories = get_category()
    footer_category = get_footer_category()
    social_media_links = get_social_links()
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
        "footer_category":footer_category,
        "hcount": hcount,
        'cart_items': cart_items,
        'cart_total': cart_total, 
    }
        
    return context


