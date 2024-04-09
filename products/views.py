from django.shortcuts import render,redirect,get_object_or_404
from .models import Product, Category, ProductReview, Cart, CartItem, ProductRentalPrice
from customerauth.models import wishlist_model, Address
from products.forms import ProductReviewForm,AddToCartForm
from django.urls import reverse
from django.db.models import Avg
from main.models import SocialMedia
from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.decorators import decorator_from_middleware
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import iyzipay
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
import json
import requests

csrf_protect = decorator_from_middleware(CsrfViewMiddleware)



def product_detail_view(request, product_slug):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    add_to_cart_form = AddToCartForm(request.POST, product_id=product.id)
    wcount=0
    hcount =0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        hcount = Cart.objects.filter(user=request.user, order_completed=False).count()

    
    reviews = ProductReview.objects.filter(product=product)
    wishCount = wishlist_model.objects.filter(product=product)
    if wishCount.exists():
        wish_count = wishCount.count()
    else:
        wish_count = 0

    average_rating = int(reviews.aggregate(Avg('rating'))['rating__avg'] or 0)

    context = {
        'product': product,
        'main_categories':main_categories,
        'wcount':wcount,
        'hcount':hcount,
        'reviews':reviews,
        'average_rating':average_rating,
        'wishCount': wish_count,
        "social_media_links":social_media_links,
        "add_to_cart_form":add_to_cart_form
    }
    
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
    if not request.user.is_authenticated:
        return redirect()
    if request.method == 'POST':
        # Formu oluştur ve gelen verileri kontrol et
        add_to_cart_form = AddToCartForm(request.POST)
        product = get_object_or_404(Product, pk=product_id)
        if add_to_cart_form.is_valid():
            product_id = add_to_cart_form.cleaned_data['product_id']
            price_type = add_to_cart_form.cleaned_data['price_type']
            quantity = add_to_cart_form.cleaned_data['quantity']
            rental_period_id = add_to_cart_form.cleaned_data['rental_period']
            cart, created = Cart.objects.get_or_create(user=request.user, order_completed=False)

            cart_item_exists = CartItem.objects.filter(cart__user=request.user, product=product, order_completed=False).exists()
            
            if cart_item_exists:
                messages.warning(request, "Ürün Sepetinizde Ekli!")
                return redirect('products:product-detail-view', product_slug=product.slug )
            # Sepete ürünü ekle
            cart_item = CartItem(cart=cart, product=product, quantity=quantity)
            if price_type == 'rental':
                rental_period = get_object_or_404(ProductRentalPrice, name=rental_period_id, product = product_id)
                cart_item.rental_price = rental_period.rental_price
                cart_item.is_rental = True
                cart_item.rental_period = rental_period.name
            else:
                cart_item.selling_price = product.selling_price

            cart_item.save()

            messages.success(request, "Ürün başarılı bir şekilde eklendi.")
            return redirect('products:product-detail-view', product_slug=product.slug )
        else:            
            messages.warning(request, "Ürünü sepete eklenirken bir sorun oluştu!")
            return redirect('products:product-detail-view', product_slug=product.slug )

    # POST isteği değilse, uygun bir hata yanıtı döndür
    return redirect('main:home')

@login_required(login_url='customerauth:sign-in')
def order_shopping_card(request):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount = 0
    hcount = 0
    cart_items = []
    cart_total = 0  # Sepetin toplam tutarı

    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        handbag = Cart.objects.get(user=request.user, order_completed=False)
        hcount = CartItem.objects.filter(cart=handbag).count()

        # Sepete eklenen ürünleri al
        cart = Cart.objects.get(user=request.user, order_completed=False)
        cart_items = cart.cartitem_set.all()

        # Sepetin toplam tutarını hesapla
        for cart_item in cart_items:
            if cart_item.is_rental:
                cart_total += cart_item.rental_price * cart_item.quantity
            else:
                cart_total += cart_item.selling_price * cart_item.quantity

    context = {
        'main_categories': main_categories,
        'wcount': wcount,
        'hcount': hcount,
        'cart_items': cart_items,
        'cart_total': cart_total,  # Sepetin toplam tutarı
        "social_media_links": social_media_links,
    }

    return render(request, 'core/order-shopping-card.html', context)

@csrf_protect
@login_required(login_url='customerauth:sign-in')
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.delete()  
        messages.success(request, "Ürün başarılı bir şekilde sepetten silindi!")
        return redirect('products:order_shopping_card')
    except:
        
        messages.warning(request, "Ürün silinnirken bir hata oluştu!")
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
    user_addresses = Address.objects.filter(user=request.user)
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        handbag = Cart.objects.get(user=request.user, order_completed=False)
        hcount = CartItem.objects.filter(cart=handbag).count()

        # Sepete eklenen ürünleri al
        cart = Cart.objects.get(user=request.user, order_completed=False)
        cart_items = cart.cartitem_set.all()

        # Sepetin toplam tutarını hesapla
        for cart_item in cart_items:
            if cart_item.is_rental:
                cart_total += cart_item.rental_price * cart_item.quantity
            else:
                cart_total += cart_item.selling_price * cart_item.quantity

    context = {
        'main_categories': main_categories,
        'wcount': wcount,
        'hcount': hcount,
        'cart_items': cart_items,
        'cart_total': cart_total,  # Sepetin toplam tutarı
        "social_media_links": social_media_links,
        "user_addresses":user_addresses
    }

    return render(request, 'core/order-check-out.html', context)






#########PaymentMethods################

api_key = 'sandbox-etkBOaBAec7Zh6jLDL59Gng0xJV2o1tV'
secret_key = 'sandbox-uC9ysXfBn2syo7ZMOW2ywhYoc9z9hTHh'
base_url = 'sandbox-api.iyzipay.com'


options = {
    'api_key': api_key,
    'secret_key': secret_key,
    'base_url': base_url
}
sozlukToken = list()

def payment(request):
    context = dict()

    buyer={
        'id': 'BY789',
        'name': 'John',
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'email@email.com',
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address={
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items=[
        {
            'id': 'BI101',
            'name': 'Binocular',
            'category1': 'Collectibles',
            'category2': 'Accessories',
            'itemType': 'PHYSICAL',
            'price': '0.3'
        },
        {
            'id': 'BI102',
            'name': 'Game code',
            'category1': 'Game',
            'category2': 'Online Game Items',
            'itemType': 'VIRTUAL',
            'price': '0.5'
        },
        {
            'id': 'BI103',
            'name': 'Usb',
            'category1': 'Electronics',
            'category2': 'Usb / Cable',
            'itemType': 'PHYSICAL',
            'price': '0.2'
        }
    ]

    request={
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '1',
        'paidPrice': '1.2',
        'currency': 'TRY',
        'basketId': 'B67832',
        'paymentGroup': 'PRODUCT',
        "callbackUrl": "http://localhost:8008/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,
        # 'debitCardAllowed': True
    }

    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)

    #print(checkout_form_initialize.read().decode('utf-8'))
    page = checkout_form_initialize
    header = {'Content-Type': 'application/json'}
    content = checkout_form_initialize.read().decode('utf-8')
    json_content = json.loads(content)
    print(type(json_content))
    print(json_content["checkoutFormContent"])
    print("************************")
    print(json_content["token"])
    print("************************")
    sozlukToken.append(json_content["token"])
    return HttpResponse(json_content["checkoutFormContent"])

@csrf_exempt
def result(request):
    context = dict()

    url = request.META.get('index')

    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'token': sozlukToken[0]
    }
    checkout_form_result = iyzipay.CheckoutForm().retrieve(request, options)
    print("************************")
    print(type(checkout_form_result))
    result = checkout_form_result.read().decode('utf-8')
    print("************************")
    print(sozlukToken[0])   # Form oluşturulduğunda 
    print("************************")
    print("************************")
    sonuc = json.loads(result, object_pairs_hook=list)
    #print(sonuc[0][1])  # İşlem sonuç Durumu dönüyor
    #print(sonuc[5][1])   # Test ödeme tutarı
    print("************************")
    for i in sonuc:
        print(i)
    print("************************")
    print(sozlukToken)
    print("************************")
    if sonuc[0][1] == 'success':
        context['success'] = 'Başarılı İŞLEMLER'
        return HttpResponseRedirect(reverse('success'), context)

    elif sonuc[0][1] == 'failure':
        context['failure'] = 'Başarısız'
        return HttpResponseRedirect(reverse('failure'), context)

    return HttpResponse(url)

