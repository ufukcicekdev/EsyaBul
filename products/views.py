from django.shortcuts import render,redirect,get_object_or_404
from .models import Product, Category, ProductReview, Cart, CartItem, ProductRentalPrice
from customerauth.models import wishlist_model, Address, User, Order, OrderItem
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
from cities_light.models import City, Country, SubRegion
from ipware import get_client_ip
from datetime import datetime
import random
import string
from django.core.mail import send_mail,EmailMultiAlternatives,EmailMessage
import os
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from dotenv import load_dotenv
from main.mainContent import mainContent

load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')


csrf_protect = decorator_from_middleware(CsrfViewMiddleware)



def product_detail_view(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    related_products = Product.objects.filter(category_id=product.category_id).exclude(id=product.id).order_by('?')[:10]
    add_to_cart_form = AddToCartForm(request.POST, product_id=product.id)
    reviews = ProductReview.objects.filter(product=product)
    wishCount = wishlist_model.objects.filter(product=product)
    mainContext = mainContent(request)
    if wishCount.exists():
        wish_count = wishCount.count()
    else:
        wish_count = 0

    average_rating = int(reviews.aggregate(Avg('rating'))['rating__avg'] or 0)

    context = {
        'product': product,
        'reviews':reviews,
        'average_rating':average_rating,
        'wishCount': wish_count,
        "add_to_cart_form":add_to_cart_form,
        "related_products":related_products
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
    user_addresses = Address.objects.filter(user=request.user)
    cart_id = None  # Sepet ID'sini başlangıçta None olarak ayarlayın

    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()

        # Kullanıcının isteğe bağlı olarak tanımlanmış sepetini alın
        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
            cart_id = handbag.id
        except Cart.DoesNotExist:
            pass

        # Kullanıcının sepetindeki ürünleri alın
        cart = Cart.objects.filter(user=request.user, order_completed=False).first()
        if cart:
            cart_items = cart.cartitem_set.all()

            # Sepetin toplam tutarını hesaplayın
            for cart_item in cart_items:
                if cart_item.is_rental:
                    cart_total += cart_item.rental_price * cart_item.quantity
                else:
                    cart_total += cart_item.selling_price * cart_item.quantity

    context = {
        'main_categories': main_categories,
         "main_categories2":main_categories,
        'wcount': wcount,
        'hcount': hcount,
        'cart_items': cart_items,
        'cart_total': cart_total,  # Sepetin toplam tutarı
        "social_media_links": social_media_links,
        "user_addresses": user_addresses,
        "cart_id": cart_id,
    }

    return render(request, 'core/order-check-out.html', context)


def my_view(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        messages.warning(request, "IP'niz alınırken bir sorunn oluştur. Daha sonra tekrar deneyin.")
        return redirect('main:home')
    else:
        return client_ip




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

def generate_order_number():
    # 10 karakterlik bir rastgele sipariş numarası oluşturuyoruz
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

order_number = generate_order_number()

order_data = {}

@csrf_protect
@login_required(login_url='customerauth:sign-in')
def payment(request):
    global order_data  # payment_params değişkenini global olarak kullanabilmek için
    if not request.user.is_authenticated:
        return redirect()

    client_ip =my_view(request)
    

    selected_address_id = request.POST.get('selected_address_id')
    selected_billing_address_id = request.POST.get('selected_billing_address_id')
    card_id = request.POST.get('card_id')
    order_total = request.POST.get('order_total')


    user_order_addresses = Address.objects.get(user=request.user, id=selected_address_id)
    order_city_id = user_order_addresses.city_id
    order_region_id = user_order_addresses.region_id
    userInfo = get_object_or_404(User, id=request.user.id)
    order_city = City.objects.get(pk=order_city_id)
    order_country = Country.objects.get(pk=order_city.country_id)
    order_subregion = SubRegion.objects.get(id=user_order_addresses.region_id)


    address_parts = [
            user_order_addresses.address_line1,
            order_city.name,
            order_subregion.name,
            order_country.name
    ]
    order_completed_order_address = ' '.join(filter(None, address_parts))



    if selected_billing_address_id:
        user_billing_addresses = Address.objects.filter(user=request.user, id=selected_billing_address_id)
        billing_city_id = user_billing_addresses.city_id
        billing_country_id = user_billing_addresses.region_id
        billing_city = City.objects.get(pk=billing_city_id)
        billing_subregion = SubRegion.objects.get(id=user_billing_addresses.region_id)
        billing_country = Country.objects.get(pk=billing_country_id)

        address_parts = [
            user_billing_addresses.address_line1,
            billing_city.name,
            billing_subregion.name,
            billing_country.name
        ]
        order_completed_billing_address = ' '.join(filter(None, address_parts))


        billing_address = {
            'contactName': user_billing_addresses.username,
            'city': billing_city.name,
            'country': billing_country.name,
            'address': user_billing_addresses.address_line1,
            'zipCode': user_billing_addresses.postal_code,
        }
    else:
        # Fatura adresi seçilmemişse, sipariş adresini kullan
        billing_address = {
            'contactName': user_order_addresses.username,
            'city': order_city.name,
            'country': order_country.name,
            'address': user_order_addresses.address_line1,
            'zipCode': user_order_addresses.postal_code,
        }

        address_parts = [
            user_order_addresses.address_line1,
            order_city.name,
            order_subregion.name,
            order_country.name
        ]
        order_completed_billing_address = ' '.join(filter(None, address_parts))

    

    cart = Cart.objects.get(user=request.user, order_completed=False, id=card_id)
    cart_items = cart.cartitem_set.all()

    current_user = request.user
    
    last_login_date = current_user.last_login.strftime("%Y-%m-%d %H:%M:%S")

    registration_date = current_user.date_joined.strftime("%Y-%m-%d %H:%M:%S")

    context = dict()

    buyer={
        'id': request.user.id,
        'name': request.user.first_name,
        'surname': request.user.last_name,
        'gsmNumber': '+9' + userInfo.phone,
        'email': request.user.email,
        'identityNumber': userInfo.tckn,
        'lastLoginDate': last_login_date,
        'registrationDate': registration_date,
        'registrationAddress': user_order_addresses.address_line1,
        'ip': client_ip,
        'city': order_city.name,
        'country': order_country.name,
        'zipCode': user_order_addresses.postal_code
    }

    order_address = {
        'contactName': user_order_addresses.username,
        'city': order_city.name,
        'country': order_country.name,
        'address': user_order_addresses.address_line1,
        'zipCode': user_order_addresses.postal_code,
    }

    cart = Cart.objects.get(user=request.user, order_completed=False, id=card_id)
    cart_items = cart.cartitem_set.all()    

    basket_items = []

    for cart_item in cart_items:
        product = cart_item.product
        
        if cart_item.is_rental:
            selling_price = cart_item.rental_price
        else:
            selling_price = cart_item.selling_price

        item = {
            'id': product.id,
            'name': product.name,
            'category1': product.get_category_breadcrumb(),  # Ürünün birincil kategorisi
            'category2':    product.get_category_breadcrumb(),  # Ürünün ikincil kategorisi (varsa)
            'itemType': 'PHYSICAL',
            'price': str(selling_price)
            # Diğer gerekli bilgileri de buradan alabilirsiniz
        }

        basket_items.append(item)

    order_data = {
        'user': request.user,
        'order_completed_order_address': order_completed_order_address,
        'order_completed_billing_address': order_completed_billing_address,
        'basket_items': basket_items,
        'order_total': order_total,
        "cart_items":cart_items,
        "card_id": card_id
    }

    request={
        'locale': 'tr',
        'conversationId': order_number,
        'price': str(order_total.replace(',','.')),
        'paidPrice': str(order_total.replace(',','.')),
        'currency': 'TRY',
        'basketId': card_id,
        'paymentGroup': 'PRODUCT',
        "callbackUrl": "http://127.0.0.1:8000/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': order_address,
        'billingAddress': billing_address,
        'basketItems': basket_items,
        #'debitCardAllowed': True
    }


    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)

    #print(checkout_form_initialize.read().decode('utf-8'))
    page = checkout_form_initialize
    header = {'Content-Type': 'application/json'}
    content = checkout_form_initialize.read().decode('utf-8')
    json_content = json.loads(content)
    sozlukToken.append(json_content["token"])
    return HttpResponse(json_content["checkoutFormContent"])

@csrf_exempt
def result(request):
    global order_data  # payment_params d
    context = dict()

    user = order_data.get('user')
    order_completed_order_address = order_data.get('order_completed_order_address')
    order_completed_billing_address = order_data.get('order_completed_billing_address')
    basket_items = order_data.get('basket_items')
    order_total = order_data.get('order_total')
    cart_items = order_data.get('cart_items')
    card_id = order_data.get('card_id')
    url = request.META.get('index')

    request_data = {
        'locale': 'tr',
        'conversationId': order_number,
        'token': sozlukToken[0]
    }
    checkout_form_result = iyzipay.CheckoutForm().retrieve(request_data, options)
    result = checkout_form_result.read().decode('utf-8')
    sonuc = json.loads(result, object_pairs_hook=list)
    if sonuc:
        if sonuc[0][1] == 'success':
            messages.success(request, "Ödeme işleminiz başarıyla gerçekleşti!")
            create_order_and_items(user, order_completed_order_address, order_completed_billing_address, basket_items, order_total, order_number, cart_items, card_id)

            order = Order.objects.get(order_number=order_number)
            order.status = 'Pending'
            order.save()
            return redirect('products:order_shopping_card')
        elif sonuc[0][1] == 'failure':
            messages.warning(request, sonuc[2][1])
    else:
        messages.warning(request, "Ödeme sırasında bir hata oluştu. Lütfen tekrar deneyin.")

    return redirect('products:order_checkout')



def create_order_and_items(user, order_completed_order_address, order_completed_billing_address, basket_items, order_total, order_number, cart_items, card_id):
    # Yeni bir sipariş oluştur
    order = Order.objects.create(
        user=user,
        order_adress=order_completed_order_address,
        billing_adress=order_completed_billing_address,
        order_details=json.dumps(basket_items),
        total_amount=float(order_total.replace(',', '.')),
        order_number=order_number,
        status='Pending',
        shipping_status='Preparing'
    )
    order_create_mail(order_number)
    cart_order_completed(card_id)
    #order_user_mail(order_number, user, card_id)
    for cart_item in cart_items:
        print("cart_item",cart_item)
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            rental_price= cart_item.rental_price,
            selling_price= cart_item.selling_price,
            is_rental=cart_item.is_rental,
            rental_period=cart_item.rental_period,
        )

    return order

def order_create_mail(order_number):
    subject = "Yeni bir sipariş oluşturuldu"
    body = f"{order_number} sipariş numaralı yeni bir sipariş oluşturuldu."

    recipients = get_user_model().objects.filter(is_superuser=True).values_list('email', flat=True)

    # E-posta gönderme işlemi
    email = EmailMessage(subject, body, EMAIL_HOST_USER, recipients)
    email.send()

def cart_order_completed(card_id):
    cart = Cart.objects.get(order_completed=False, id=card_id)
    cart.order_completed = True
    cart.save()

    cart_items = CartItem.objects.get(order_completed=False, cart_id=card_id)
    cart_items.order_completed = True
    cart_items.save()




def order_user_mail(order_number, user, card_id):
    subject = 'Sipariş Alındı'
    cart_items = []
    cart_total = 0  

    cart = Cart.objects.get(user=user, id=card_id)
    if cart:
        cart_items = cart.cartitem_set.all()

        # Sepetin toplam tutarını hesaplayın
        for cart_item in cart_items:
            if cart_item.is_rental:
                cart_total += cart_item.rental_price * cart_item.quantity
            else:
                cart_total += cart_item.selling_price * cart_item.quantity

    context = {
        'subject':subject,
        'username': user.username,
        'cart_total': cart_total,  
        "order_number":order_number
    }


    email_content = render_to_string('email_templates/order_checkout.html', context)
    email = EmailMessage(subject, email_content,EMAIL_HOST_USER, to=[user.email])
    email.content_subtype = 'html' 
    email.send()
