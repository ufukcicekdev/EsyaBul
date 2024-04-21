from customerauth.models import wishlist_model
from main.models import SocialMedia
from products.models import Cart, CartItem, Category


def mainContent(request):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount = 0
    hcount=0

    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
        except Cart.DoesNotExist:
            pass
        
    context = {
        'social_media_links': social_media_links, 
        "wcount": wcount, 
        'main_categories':main_categories,
        "hcount":hcount,
        "main_categories2":main_categories,
        "main_categories4":main_categories,
    }
        
    return context