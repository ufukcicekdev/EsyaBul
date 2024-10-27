from django.shortcuts import render,redirect,get_object_or_404
from .models import Product, Category, ProductReview, Cart, CartItem, ProductRentalPrice
from customerauth.models import wishlist_model, Address, User, UserProductView
from products.forms import ProductReviewForm,AddToCartForm
from django.db.models import Avg
from main.models import SocialMedia
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.decorators import decorator_from_middleware
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from dotenv import load_dotenv
from main.mainContent import mainContent
from django.views.decorators.cache import cache_page
from django.utils import timezone

load_dotenv()


csrf_protect = decorator_from_middleware(CsrfViewMiddleware)


def product_detail_view(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    related_products = Product.objects.filter(is_active=True, category_id=product.category_id).exclude(id=product.id).order_by('?')[:10]
    add_to_cart_form = AddToCartForm(request.POST, product_id=product.id)
    reviews = ProductReview.objects.filter(product=product)
    wishCount = wishlist_model.objects.filter(product=product)
    mainContext = mainContent(request)

    wish_count = wishCount.count() if wishCount.exists() else 0

    average_rating = int(reviews.aggregate(Avg('rating'))['rating__avg'] or 0)
    
    if request.user.is_authenticated:
        user_product_view, created = UserProductView.objects.get_or_create(user=request.user, product=product)
        if not created:
            user_product_view.created_date = timezone.now()
            user_product_view.save()

    # İlgili ürünlerin görselleriyle birlikte alınması
    related_products_list = product.related.all()
    related_products_with_images = []
    for related_product in related_products_list:
        images = related_product.related_products.all()  # Burada `related_products` ile görselleri alıyoruz
        related_products_with_images.append({
            'product': related_product,
            'images': images
        })

    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'wishCount': wish_count,
        'add_to_cart_form': add_to_cart_form,
        'related_products': related_products,
        'related_products_list': related_products_list,
        'related_products_with_images': related_products_with_images,
    }
    context.update(mainContext)
    
    return render(request, 'core/product-detail.html', context)





@login_required(login_url='customerauth:sign-in')
def add_product_review(request, product_id):
    if not request.user.is_authenticated:
        return redirect()

    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('products:product-detail-view', product_slug=product.slug )
    else:
        form = ProductReviewForm()
    return redirect('main:home')



@login_required(login_url='customerauth:sign-in')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        add_to_cart_form = AddToCartForm(request.POST, product_id=product_id)
        product = get_object_or_404(Product, pk=product_id)
        
        if add_to_cart_form.is_valid():
            price_type = add_to_cart_form.cleaned_data['price_type']
            quantity = add_to_cart_form.cleaned_data['quantity']
            rental_period_id = add_to_cart_form.cleaned_data.get('rental_period')

            active_cart = Cart.objects.filter(user=request.user, order_completed=False).first()
            if not active_cart:
                active_cart = Cart.objects.create(user=request.user, order_completed=False)

            
            existing_item = CartItem.objects.filter(
                cart=active_cart,
                product=product,
                order_completed=False
            ).first()

              
            if existing_item:
                messages.warning(request, f"Bu ürün zaten sepette { 'kiralama' if price_type == 'rental' else 'satın alma' } olarak mevcut!")
                return redirect('products:product-detail-view', product_slug=product.slug)


            # Yeni bir CartItem oluştur
            cart_item = CartItem(cart=active_cart, product=product, quantity=quantity)
            
            if price_type == 'rental':
                rental_period = get_object_or_404(ProductRentalPrice, id=rental_period_id, product=product)
                cart_item.rental_price = rental_period.rental_price
                cart_item.is_rental = True
                cart_item.rental_period = rental_period.name
            else:
                cart_item.selling_price = product.selling_price

            cart_item.save()

            messages.success(request, "Ürün başarılı bir şekilde eklendi.")
            return redirect('products:product-detail-view', product_slug=product.slug)
        else:            
            messages.warning(request, "Ürünü sepete eklerken bir sorun oluştu!")
            return redirect('products:product-detail-view', product_slug=product.slug)
    else:
        # Eğer istek POST metoduyla değilse, ana sayfaya yönlendir
        return redirect('main:home')



def check_product_in_cart(user, product_id):
    cart_item_exists = CartItem.objects.filter(cart__user=user, product_id=product_id, order_completed=False).exists()
    return cart_item_exists

@login_required(login_url='customerauth:sign-in')
def order_shopping_card(request):
    mainContext = mainContent(request)
    cart_items = []
    cart_total = 0 
    user_verified = False

    if request.user.is_authenticated:
        user_verified = get_object_or_404(User, id=request.user.id).verified

        cart = Cart.objects.filter(user=request.user, order_completed=False).first()
        if cart:
            cart_items = cart.cartitem_set.all()

            for cart_item in cart_items:
                if cart_item.is_rental:
                    cart_total += cart_item.rental_price * cart_item.quantity
                else:
                    cart_total += cart_item.selling_price * cart_item.quantity
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total, 
        "user_verified": user_verified
    }
    context.update(mainContext)
    return render(request, 'core/order-shopping-card.html', context)


def update_cart_item_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if request.method == "POST":
        quantity = request.POST.get('quantity', 1)
        cart_item.quantity = quantity
        cart_item.save()
    return redirect('products:order_shopping_card')


@csrf_protect
@login_required(login_url='customerauth:sign-in')
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.delete()  
        messages.success(request, "Ürün başarılı bir şekilde sepetten silindi!")
        return redirect('products:order_shopping_card')
    except:
        
        messages.warning(request, "Ürün silinirken bir hata oluştu!")
        return redirect('products:order_shopping_card')
    
        
@csrf_protect
@login_required(login_url='customerauth:sign-in')
def order_checkout(request):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount = 0
    hcount = 0
    cart_items = []
    cart_total = 0  # Sepetin toplam tutarı
    delivery_addresses = Address.objects.filter(user=request.user, delivery_addresses=True)
    billing_addresses = Address.objects.filter(user=request.user, billing_addresses=True)

    cart_id = None  

    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()

        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
            cart_id = handbag.id
        except Cart.DoesNotExist:
            pass

        cart = Cart.objects.filter(user=request.user, order_completed=False).first()
        if cart:
            cart_items = cart.cartitem_set.all()

            # Sepetin toplam tutarını hesaplayın
            for cart_item in cart_items:
                if cart_item.is_rental:
                    cart_total += cart_item.rental_price * cart_item.quantity
                else:
                    cart_total += cart_item.selling_price * cart_item.quantity

    # Kullanıcının varsayılan adreslerini al
    default_delivery_address = delivery_addresses.first() if delivery_addresses.exists() else None
    default_billing_address = billing_addresses.first() if billing_addresses.exists() else None

    context = {
        'main_categories': main_categories,
        'wcount': wcount,
        'hcount': hcount,
        'cart_items': cart_items,
        'cart_total': cart_total,
        "social_media_links": social_media_links,
        "delivery_addresses": delivery_addresses,
        "billing_addresses": billing_addresses,
        "cart_id": cart_id,
        "default_delivery_address": default_delivery_address,
        "default_billing_address": default_billing_address,
    }

    mainContext = mainContent(request)

    context.update(mainContext)

    return render(request, 'core/order-check-out.html', context)
