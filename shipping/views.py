import requests
import random
import string
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .models import CargoStatus, ShippingOrder
from customerauth.models import Order, OrderItem, User, City, District, Neighborhood
import os
import decimal
from dotenv import load_dotenv
load_dotenv()


SHIPPING_AUTH = os.getenv('SHIPPING_AUTH')
SHIPPING_URL = os.getenv('SHIPPING_URL')

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def decimal_to_float(value):
    if isinstance(value, decimal.Decimal):
        return float(value)
    return value

def create_shipping(order_number):
    order = get_object_or_404(Order, order_number=order_number)
    order_items = OrderItem.objects.filter(order=order.id)
    total_quantity = order_items.aggregate(total=Sum('quantity'))['total']
    user = get_object_or_404(User, id=order.user.id)
    
    customer = f"{user.first_name} {user.last_name}"
    customer_code = user.id
    province_name = get_object_or_404(City, city_id=order.order_city_id)
    county_name = get_object_or_404(District, district_id=order.order_region_id)
    district = get_object_or_404(Neighborhood, neighborhood_id=order.order_neighborhood_id)
    
    address = order.billing_adress
    tax_number = user.tckn if user.tckn else ''
    telephone = user.phone
    amount = order.total_amount
    quantity = total_quantity
    total_bulk = order.calculate_total_bulk()
    verification_code = generate_verification_code()

    # API'ye gönderilecek payload
    payload = {
        "customer": customer,
        "customer_code": customer_code,
        "province_name": province_name.name,
        "county_name": county_name.name,
        "district": district.name,
        "address": address,
        "tax_number": tax_number,
        "telephone": telephone,
        "amount": decimal_to_float(amount),
        "quantity": quantity,
        "total_bulk": int(total_bulk),
        "verification_code": verification_code,
        "branch_code":"34"
    }

    # API'ye gönderme işlemini yap
    try:
        response_data = send_to_kargoturk_api(payload)
    except Exception as e:
        print(e)

    if not response_data['error']:
        # Başarılı yanıt durumunda barcode'u kaydet
        barcode = response_data['barcode'] 
        record_id = response_data['record_id'] 

        shipping_order = ShippingOrder.objects.create(
            order=order,
            customer=user,
            customer_name=customer,
            customer_code=customer_code,
            province_name=province_name.name.capitalize(),
            county_name=county_name.name.capitalize(),
            district=district.name.capitalize(),
            address=address,
            tax_number=tax_number,
            telephone=telephone,
            amount=amount,
            quantity=quantity,
            total_bulk=total_bulk,
            verification_code=verification_code,
            barcode=barcode,
            shipping_status = CargoStatus.objects.get(status_code="00"),
            record_id=record_id,
            shipping_url=SHIPPING_URL+barcode
        )
        return response_data  # Yanıtı döndür
    else:
        # Hatalı yanıt durumunda hata bilgisi döndür
        return response_data


def send_to_kargoturk_api(payload):
    headers = {
        "Authorization": SHIPPING_AUTH,
        "From":"info@esyala.com"  # Buraya uygun token'ı ekleyin
    }

    response = requests.post("http://online.kargoturk.com.tr/restapi/client/consignment/add", json=payload, headers=headers)
    json_response = response.json()
    response_status = json_response.get("code")
    response_error = json_response.get("error")

    if response_status == '200' and response_error=='false':        
        return {
            "error": False,
            "result": json_response.get("result", "Kayıt Başarılı"),
            "barcode": json_response.get("barcode", ""),
            "record_id": json_response.get("record_id", None)
        }
    else:
        # Hatalı yanıt durumunda
        return {
            "error": True,
            "result": f"Hata oluştu: {response.status_code}, Mesaj: {response.text}"
        }



def delete_consignment(barcode):

    headers = {
        "Authorization": SHIPPING_AUTH,
        "From":"info@esyala.com"  # Buraya uygun token'ı ekleyin
    }

    response = requests.delete(f"http://online.kargoturk.com.tr/restapi/client/consignment/edit/{barcode}",headers=headers)
    
    

    if response.status_code == 200:
        return {"message": "Kargo kaydı başarıyla silindi."}
    else:
        return {
            "error": "Kargo kaydı silinemedi.",
            "details": response.json(),
            "status_code": response.status_code
        }
