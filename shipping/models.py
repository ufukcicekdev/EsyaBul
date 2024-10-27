from django.db import models
from customerauth.models import *
# Create your models here.



class CargoStatus(models.Model):
    status_code = models.CharField(max_length=2, unique=True)  
    status_description = models.CharField(max_length=255) 

    def __str__(self):
        return f"{self.status_code} - {self.status_description}"


class ShippingOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipping_orders') 
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_orders') 
    customer_name = models.CharField(max_length=250, blank=True, verbose_name="Müşteri Adı") 

    customer_code = models.CharField(max_length=50, blank=True, verbose_name="Alıcı Kodu")
    province_name = models.CharField(max_length=100, verbose_name="İl")
    county_name = models.CharField(max_length=100, verbose_name="İlçe")
    district = models.CharField(max_length=100, blank=True, verbose_name="Mahalle")
    address = models.TextField(verbose_name="Adres")
    tax_number = models.CharField(max_length=50, blank=True, verbose_name="TC / Vergi No")
    tax_office = models.CharField(max_length=100, blank=True, verbose_name="Vergi Dairesi")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    

    order_number = models.CharField(max_length=20, blank=True, verbose_name="Sipariş Numarası")

    # Şube ve Kargo Bilgileri
    branch_code = models.CharField(max_length=50, default="34", verbose_name="Şube Kodu")
    start_branch = models.CharField(max_length=50, blank=True, verbose_name="Çıkış Şubesi")
    region_code = models.CharField(max_length=50, blank=True, verbose_name="Dağıtım Bölgesi Kodu")
    courrier_code = models.CharField(max_length=50, blank=True, verbose_name="Kurye Kodu")
    
    # Barkod Bilgileri
    barcode = models.CharField(max_length=100, blank=True, unique=True, verbose_name="Barkod")
    sub_barcode = models.TextField(blank=True, verbose_name="Alt Barkod")

    amount_type_id = models.IntegerField(default=3, verbose_name="Ödeme Türü")
    
    # Fatura ve Kargo Bilgileri
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tutar", blank=True, null=True)
    currency_name = models.CharField(max_length=10, default="TRY", blank=True, verbose_name="Para Birimi")
    summary = models.TextField(blank=True, verbose_name="İçerik")
    sender_note = models.TextField(blank=True, verbose_name="Gönderici Notu")
    
    quantity = models.IntegerField(default=1, verbose_name="Paket Miktar")
    weight = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, verbose_name="Ağırlık (Kg)")


    total_bulk = models.IntegerField(default=1, verbose_name="Toplam Desi")
    verification_code = models.CharField(max_length=10, verbose_name="Alıcı Teslim Şifresi")  # Verification Code alanı

    shipping_status = models.ForeignKey(CargoStatus, on_delete=models.SET_NULL, null=True) 

    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Oluşturulma tarihi
    updated_at = models.DateTimeField(auto_now=True, null=True) 
    record_id = models.CharField(max_length=50, verbose_name="Kayıt Numarası",null=True)  
    
    shipping_url = models.URLField(verbose_name="Kargo Takip Url", null=True)


    def __str__(self):
        return f"{self.customer} - {self.barcode or 'Barkodsuz'}"






class ShippingMovement(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipping_movements')  # Order ile bağlantı
    shipping_order = models.ForeignKey(ShippingOrder, on_delete=models.CASCADE, related_name='shipping_movements')  # ShippingOrder ile bağlantı
    barcode = models.CharField(max_length=100)
    sender_barcode = models.CharField(max_length=100)
    sender_name = models.CharField(max_length=100)
    acceptance_date = models.DateField()
    sender_address = models.TextField()
    sender_city = models.CharField(max_length=100, blank=True)
    sender_phone = models.CharField(max_length=15, blank=True)
    collection_fee = models.DecimalField(max_digits=10, decimal_places=2)
    weight_bulk = models.DecimalField(max_digits=10, decimal_places=2)
    package_quantity = models.IntegerField()
    recipient_name = models.CharField(max_length=100)
    status =  models.ForeignKey(CargoStatus, on_delete=models.SET_NULL, null=True) 
    status_number = models.CharField(max_length=100)
    recipient_address = models.TextField()
    recipient_district = models.CharField(max_length=100)
    recipient_city = models.CharField(max_length=100)
    result_status = models.CharField(max_length=50)
    result_description = models.TextField()
    recipient_phone = models.CharField(max_length=100)
    result_date = models.DateField()
    arrival_branch = models.CharField(max_length=100)
    exit_number = models.CharField(max_length=100)
    tracking_url = models.URLField()
    movements = models.JSONField()  # Hareketlerin saklanması için
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Oluşturulma tarihi
    updated_at = models.DateTimeField(auto_now=True, null=True) 
