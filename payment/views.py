from notification.smtp2gomailsender import send_email_via_smtp2go
import random
import string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
import json
import iyzipay
from ipware import get_client_ip
from django.contrib import messages
from cities_light.models import City, Country, SubRegion, Region
from customerauth.models import Address, Order, OrderItem, Payment, User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import os
from dotenv import load_dotenv
from esyabul.settings import base
from django.utils.decorators import decorator_from_middleware
from django.middleware.csrf import CsrfViewMiddleware
from xhtml2pdf import pisa
from products.models import Cart, CartItem
from django.template.loader import render_to_string
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from main.decorators import log_request
from main.models import Request_Log_Table
from django.http import HttpResponseRedirect
from slack_send_messages.send_messages import send_new_order_message
from django.urls import reverse
load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')


if base.DEBUG:
    callbackUrl = os.getenv('DEV_CALLBACK_URL')
    iyzco_api_key = os.getenv('DEV_API_KEY')
    iyzco_secret_key = os.getenv('DEV_SECRET_KEY')
    iyzco_base_url = os.getenv('DEV_IYZCO_BASE_URL')
else:
    callbackUrl = os.getenv('PROD_CALLBACK_URL')
    iyzco_api_key = os.getenv('PROD_API_KEY')
    iyzco_secret_key = os.getenv('PROD_SECRET_KEY')
    iyzco_base_url = os.getenv('PROD_IYZCO_BASE_URL')

csrf_protect = decorator_from_middleware(CsrfViewMiddleware)


api_key = iyzco_api_key
secret_key = iyzco_secret_key
base_url = iyzco_base_url


options = {
    'api_key': api_key,
    'secret_key': secret_key,
    'base_url': base_url
}
sozlukToken = list()


def refund_payment_cancel_order(request, reason, order_number, id, orders_detail):
    client_ip = my_view(request) 
    request = {
        'locale': 'tr',
        'conversationId': order_number,
        'paymentId': orders_detail.payment_id,
        'paymentTransactionId': orders_detail.payment_transaction_id,
        'ip': client_ip,
        'currency':'TRY',
        'price': str(orders_detail.total_amount),
        'reason': 'other',
        'description': reason
    }
    cancel = iyzipay.Refund().create(request, options)
    result = cancel.read().decode('utf-8')
    sonuc = json.loads(result, object_pairs_hook=list)
    sonuc = dict(json.loads(result))
    return True if sonuc.get('status') == 'success' else False


def my_view(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        messages.warning(request, "IP'niz alınırken bir sorun oluştur. Daha sonra tekrar deneyin.")
        return redirect('main:home')
    else:
        return client_ip



#########PaymentMethods################


def generate_order_number():
    while True:
        order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if not Order.objects.filter(order_number=order_number).exists():
            return order_number 

order_number = generate_order_number()

order_data = {}

@log_request
def payment_order(request):
    global order_data 
    if not request.user.is_authenticated:
        return redirect()
    
    if request.method != 'POST':
        return HttpResponse(status=405)

    client_ip = my_view(request)
    

    selected_address_id = request.POST.get('selected_address_id')
    selected_billing_address_id = request.POST.get('selected_billing_address_id')
    card_id = request.POST.get('card_id')
    order_total = request.POST.get('order_total')


    user_order_addresses = Address.objects.get(user=request.user, id=selected_address_id)
    order_city_id = user_order_addresses.city_id
    order_region_id = user_order_addresses.region_id
    userInfo = get_object_or_404(User, id=request.user.id)
    order_city = Region.objects.get(pk=order_city_id)
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

    context = dict()

    buyer={
        'id': userInfo.id,
        'name': userInfo.first_name,
        'surname': userInfo.last_name,
        'gsmNumber': '+9' + userInfo.phone,
        'email': userInfo.email,
        'identityNumber': userInfo.tckn,
        'lastLoginDate': userInfo.last_login.strftime("%Y-%m-%d %H:%M:%S"),
        'registrationDate': userInfo.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
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

    basket_items = create_order_items(request, card_id)

    order_data = {
        'user': request.user,
        'order_completed_order_address': order_completed_order_address,
        'order_completed_billing_address': order_completed_billing_address,
        'basket_items': basket_items,
        'order_total': order_total,
        "cart_items":cart_items,
        "card_id": card_id
    }


    request_data = create_request_data(order_number, order_total, card_id, callbackUrl, buyer, order_address, billing_address, basket_items)
    try:
        checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request_data, options)
        header = {'Content-Type': 'application/json'}
        content = checkout_form_initialize.read().decode('utf-8')
        json_content = json.loads(content)
        Request_Log_Table.objects.create(
            request_data = request_data,
            response_data=json_content,
            text = "checkout_form_initialize",
            order_number = order_number
        )
        sozlukToken.append(json_content["token"])
        return HttpResponse(json_content["checkoutFormContent"])
    except Exception as e:
        messages.error(request, "Ödeme başlatılırken bir hata oluştu: {}".format(e))
        return redirect('products:order_checkout')



def create_order_items(request, card_id):
    cart = Cart.objects.get(user=request.user, order_completed=False, id=card_id)
    cart_items = cart.cartitem_set.all()    

    basket_items = []

    for cart_item in cart_items:
        product = cart_item.product
        
        if cart_item.is_rental:
            selling_price = cart_item.rental_price
        else:
            selling_price = cart_item.selling_price
        

        breadcrumb_names = [item['name'] for item in product.get_category_breadcrumb()]
        breadcrumb_string = ','.join(breadcrumb_names)  

        item = {
            'id': product.id,
            'name': product.name,
            'category1': breadcrumb_string,
            'category2': breadcrumb_string,
            'itemType': 'PHYSICAL',
            'price': str(selling_price)
        }

        basket_items.append(item)

    return basket_items

def create_request_data(order_number, order_total, card_id, callbackUrl, buyer, order_address, billing_address, basket_items):
    request={
        'locale': 'tr',
        'conversationId': order_number,
        'price': str(order_total.replace(',','.')),
        'paidPrice': str(order_total.replace(',','.')),
        'currency': 'TRY',
        'basketId': card_id,
        'paymentGroup': 'PRODUCT',
        "callbackUrl":  callbackUrl + "/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': order_address,
        'billingAddress': billing_address,
        'basketItems': basket_items,
    }
    # if base.DEBUG == False:
    #     request.update({'debitCardAllowed': True})

    return request



@require_http_methods(["POST"])
@csrf_exempt
@log_request
def result(request):
    global order_data 
    context = dict()

    if request.method != 'POST':
        return HttpResponse(status=405)

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

    try:
        checkout_form_result = iyzipay.CheckoutForm().retrieve(request_data, options)
        result = checkout_form_result.read().decode('utf-8')
        sonuc = json.loads(result)
        Request_Log_Table.objects.create(
            request_data = request_data,
            response_data=sonuc,
            text = "checkout_form_result",
            order_number = order_number
        )
        if sonuc and sonuc['status'] == 'success':
            messages.success(request, "Ödeme işleminiz başarıyla gerçekleşti!")
            payment_transaction_id = get_payment_transaction_id(sonuc)
            create_order_and_items(user, order_completed_order_address, order_completed_billing_address, basket_items, order_total, order_number, cart_items, card_id, payment_transaction_id)
            generate_and_upload_pdf(order_number)
            order = Order.objects.get(order_number=order_number)
            order.status = 'Pending'
            order.payment_id = sonuc['paymentId']
            order.payment_transaction_id = payment_transaction_id
            order.save()
            #send_new_order_message(order, order_total)

            create_payment_object(user, sonuc)
            return HttpResponseRedirect(reverse('products:order_shopping_card'))

        elif sonuc and sonuc['status'] == 'failure':
            messages.warning(request, sonuc['errorMessage'])
        else:
            messages.warning(request, "Ödeme sırasında bir hata oluştu. Lütfen tekrar deneyin.")

    except Exception as e:
        messages.error(request, "Ödeme sonucu alınırken bir hata oluştu: {}".format(e))

    return HttpResponseRedirect(reverse('products:order_checkout'))




def get_payment_transaction_id(sonuc):
    transaction_id =""
    item_transactions = sonuc.get('itemTransactions', [])
    for transaction in item_transactions:
        payment_transaction_id = transaction.get('paymentTransactionId')
        if payment_transaction_id:
            transaction_id = payment_transaction_id
            break
    
    return transaction_id


def create_payment_object(user, sonuc):
    Payment.objects.create(
        user=user,
        status=sonuc['status'] ,
        json_data=sonuc  
    )



def create_order_and_items(user, order_completed_order_address, order_completed_billing_address, basket_items, order_total, order_number, cart_items, card_id, payment_transaction_id):
    
    order = Order.objects.create(
        user=user,
        order_adress=order_completed_order_address,
        billing_adress=order_completed_billing_address,
        order_details=json.dumps(basket_items),
        total_amount=float(order_total.replace(',', '.')),
        order_number=order_number,
        status='Pending',
        shipping_status='Preparing',
        payment_transaction_id = payment_transaction_id
    )
    
    order_create_mail(order_number, user)
    cart_order_completed(card_id)
    order_user_mail(order_number, user, card_id)
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            rental_price= cart_item.rental_price,
            selling_price= cart_item.selling_price,
            is_rental=cart_item.is_rental,
            rental_period=cart_item.rental_period,
        )




def generate_and_upload_pdf(order_number):
    order = get_object_or_404(Order, order_number=order_number)
    order_items = order.order_items.all()
    html_content = render_to_string('pdfTemplates/order_pdf_template.html', {'order': order, 'order_items': order_items})
    pdf_file = ContentFile(b"")
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    file_name = f'{order_number}.pdf'  
    file_path = default_storage.save(f'order_pdf_documents/{file_name}', pdf_file)
    order.order_pdf_document = file_path
    order.save()



def order_create_mail(order_number, user):
    subject = "Yeni bir sipariş oluşturuldu"

    email_content = render_to_string('email_templates/order_create_mail.html', {
        'subject':subject,
        'username': user.username,
        "order_number":order_number
    })
    
    recipients_queryset = get_user_model().objects.filter(is_superuser=True).values_list('email', flat=True)
    recipients = list(recipients_queryset)

    send_email_via_smtp2go(recipients, subject, email_content)

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


    email_content = render_to_string('email_templates/order_checkout.html', {
        'subject':subject,
        'username': user.username,
        'cart_total': cart_total,  
        "order_number":order_number
    })
    send_email_via_smtp2go([user.email], subject, email_content)
