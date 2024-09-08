from django.shortcuts import redirect, render, get_object_or_404
from customerauth.forms import UserRegisterForm, ProfileForm, AddressForm,CustomPasswordChangeForm, NotificationSettingsForm,CancelOrderForm,EmailChangeForm
from django.contrib.auth import login, authenticate, logout, get_backends
from django.contrib import messages
from django.conf import settings
from customerauth.models import User, Address, MyStyles, wishlist_model,Order,OrderItem
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from products.models import RoomType, HomeType, HomeModel, SpaceDefinition, TimeRange, Product, Category,Cart,CartItem
from actstream import action
from notification.smtp2gomailsender import send_email_via_smtp2go
import json
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.core import serializers
from django.template.loader import render_to_string
from cities_light.models import Country, City, Region, SubRegion
from main.models import SocialMedia,HomeSubBanner
from .tcknrequest import TCKimlikNoSorgula
import iyzipay
from ipware import get_client_ip
from payment.views import refund_payment_cancel_order
from main.mainContent import mainContent
from main.decorators import log_request

from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from customerauth.send_confirmation import send_confirmation_email, send_email_change_notification


def confirm_email(request, uidb64, token):
    context = {}
    mainContext = mainContent(request)
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            user.email_verified = True
            user.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            context['message'] = "E-posta adresiniz başarıyla doğrulandı ve otomatik olarak giriş yaptınız!"
            context.update(mainContext)
        else:
            context['message'] = "E-posta doğrulama bağlantısı geçersiz."
            context.update(mainContext)
    except User.DoesNotExist:
        context['message'] = "Kullanıcı bulunamadı."
        context.update(mainContext)

    return render(request, 'customerauth/confirmation_result.html', context)




def register_view(request):
    
    homesubbanners = HomeSubBanner.objects.filter(is_active=True)
    mainContext = mainContent(request)
    
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            
            send_confirmation_email(new_user, request)
            
            messages.success(request, "Kaydınız başarılı! E-posta adresinizi doğrulamak için lütfen e-postanızı kontrol edin.")
            return redirect("customerauth:sign-in")
        else:
            # Hataları döngüyle işle ve uygun mesajı göster
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = {
                        'password2': 'Şifre Tekrar',
                        'password1': 'Şifre',
                        'username': 'Kullanıcı Adı',
                        'email': 'Email'
                    }.get(field, field.capitalize())
                    messages.warning(request, f"{field_name}: {error}")
            return redirect("customerauth:sign-up")
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
        "homesubbanners": homesubbanners
    }
    context.update(mainContext)
    
    return render(request, "customerauth/sign-up.html", context)


def login_view(request):
    homesubbanners = HomeSubBanner.objects.filter(is_active=True)
    mainContext = mainContent(request)
    
    if request.user.is_authenticated:
        action.send(request.user, verb='login')
        user_name = request.user.username 
        context1 = {
            'success_messages': f"Tekrar hoşgeldiniz, {user_name}!",
            'target_url': "main:home",
        }
        context1.update(mainContext)
        return render(request, "customerauth/thank-you.html", context1)
    
    if request.method == "POST":
        email_or_username = request.POST.get("email_or_username")
        password = request.POST.get("password")
        
        try:
            user = User.objects.get(email=email_or_username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                messages.warning(request, "Hatalı şifre veya kullanıcı adı girdiniz.")
                return render(request, "customerauth/sign-in.html", {"homesubbanners": homesubbanners, **mainContext})

        if not user.email_verified:
            
            send_confirmation_email(user, request)
            messages.warning(request, "E-posta adresiniz doğrulanmamış. Yeni bir doğrulama e-postası gönderildi. Lütfen e-postanızı kontrol edin.")
            return render(request, "customerauth/sign-in.html", {"homesubbanners": homesubbanners, **mainContext})

        user = authenticate(request, email=user.email, password=password)
        if user is not None:
            login(request, user)
            user_name = request.user.username 
            
            context1 = {
                'success_messages': f"Tekrar hoşgeldiniz, {user_name}!",
                'target_url': "main:home",
                "homesubbanners": homesubbanners
            }
            context1.update(mainContext)
            action.send(request.user, verb='login')
            return render(request, "customerauth/thank-you.html", context1)
        else:
            messages.warning(request, "Hatalı şifre veya kullanıcı adı girdiniz.")

    context = {
        "homesubbanners": homesubbanners
    }
    context.update(mainContext)
    return render(request, "customerauth/sign-in.html", context)
        

def logout_view(request):
    social_media_links = SocialMedia.objects.all()
    action.send(request.user , verb='logout')
    logout(request)
    context1 = {
        'success_messages': "Tekrar görüşmek üzere!",
        'target_url':"main:home",
        "social_media_links":social_media_links
    }
    return render(request, "customerauth/thank-you.html", context1)

@login_required(login_url='customerauth:sign-in')
def profile_update(request):
    title = "Hesabım"
    profile = get_object_or_404(User, id=request.user.id)
    
    mainContext = mainContent(request)
    
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # formu doğrulamadan önce kaydet
            tc_kimlik_no = form.cleaned_data['tckn']
            ad = form.cleaned_data['first_name']
            soyad = form.cleaned_data['last_name']
            dogum_yili = form.cleaned_data['birth_date'].year 
            sorgu = TCKimlikNoSorgula(tc_kimlik_no, ad, soyad, dogum_yili)
            sonuc = sorgu.sorgula()
            if sonuc:
                profile.verified = True  
                profile.save() 
                messages.success(request, "Profiliniz başarıyla güncellendi.")
                return redirect("customerauth:profile")
            else:
                messages.error(request, "TC Kimlik No doğrulanamadı. Lütfen bilgilerinizi kontrol edin.")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
        "title": title,
    }
    context.update(mainContext)

    return render(request, "customerauth/profile-edit.html", context)


@login_required(login_url='customerauth:sign-in')
def thank_you_view(request):
    user_name = request.user.username 
    mainContext = mainContent(request)
    context = {
        'user_name': user_name, 
    }
    context.update(mainContext)
    return render(request, "customerauth/thank-you.html", context)


@login_required(login_url='customerauth:sign-in')
def customer_dashboard(request):
    user_profile = get_object_or_404(User, id=request.user.id)
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm(request.POST or None) 
    title ="Hesabım"
    mainContext = mainContent(request)
    if request.method == "POST":
        if form.is_valid():  
            new_address = form.save(commit=False) 
            new_address.user = request.user 
            new_address.save()
            messages.success(request, "Profiliniz Başarı ile Güncellenmiştir.")
            return redirect("customerauth:dashboard")
        else:
            messages.error(request, "There was an error with the form.")

    context = {
        "user_profile": user_profile,
        "addresses": addresses,
        "form": form ,
        "title":title,
    }
    context.update(mainContext)
    return render(request, 'customerauth/dashboard.html', context)


@login_required(login_url='customerauth:sign-in')
def password_change(request):
    title = "Hesabım"
    mainContext = mainContent(request)
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, "Password changed successfully.")
            return redirect("customerauth:dashboard")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomPasswordChangeForm(request.user)
        
    context = {
        "form": form,
        "title":title,
    }
    context.update(mainContext)
    return render(request, 'customerauth/password_change.html', context)


@login_required(login_url='customerauth:sign-in')
def notifications(request):
    title="Bildirimlerim"
    user_profile = get_object_or_404(User, id=request.user.id)
    mainContext = mainContent(request)
    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification settings updated successfully.')
            return redirect("customerauth:notifications")
        else:
            messages.error(request, 'Error updating notification settings. Please check the form.')
    else:
        form = NotificationSettingsForm(instance=user_profile)

    context = {
        'form': form, 
        'title':title, 
    }
    context.update(mainContext)
    return render(request, 'customerauth/notifications.html', context)

###################### Address  Open #################

@login_required(login_url='customerauth:sign-in')
def address_list(request):
    title ="Adreslerim"
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm(request.POST or None) 
    mainContext = mainContent(request)
    context = {
        'addresses': addresses, 
        'form': form, 
        'title':title ,
    }
    context.update(mainContext)
    return render(request, 'customerauth/address.html', context)


@login_required(login_url='customerauth:sign-in')
def create_address(request):
    title ="Adreslerim"
    mainContext = mainContent(request)    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()
            messages.success(request,"Adresiniz Başarıyla Eklenmiştir.")
            return redirect('customerauth:address-list')  
        else:
            print("form error: ", form.errors)
    else:
        form = AddressForm()

    context = {
        'form': form, 
        'title': title, 
    }
    context.update(mainContext)
    return render(request, 'customerauth/add-new-address.html', context)


@login_required(login_url='customerauth:sign-in')
def edit_address(request, address_id):
    title ="Adreslerim"
    address = get_object_or_404(Address, id=address_id)
    mainContext = mainContent(request)  
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request,"Adresiniz Başarıyla Güncellenmiştir.")
            return redirect('customerauth:address-list')
    else:
        form = AddressForm(instance=address)

    context = {
        'form': form, 
        'address': address, 
        'title': title,   
    }
    context.update(mainContext)
    return render(request, 'customerauth/edit-address.html', context)


@login_required(login_url='customerauth:sign-in')
def delete_address(request, address_id):

    address = get_object_or_404(Address, id=address_id)
    address.delete()
    messages.success(request, "Adresiniz başarıyla silinmiştir.")
    return redirect('customerauth:address-list')


@login_required(login_url='customerauth:sign-in')
def get_subregions(request):
    if request.method == 'GET':
        city_id = request.GET.get('city_id')
        if city_id:
            subregions = SubRegion.objects.filter(region_id=city_id).values('id', 'name')
            data = {str(subregion['id']): subregion['name'] for subregion in subregions}
            return JsonResponse(data)

    return JsonResponse({})

###################### My Style  Open #################

@login_required(login_url='customerauth:sign-in')
def room_type_selected(request):
    active_room_types = RoomType.objects.filter(is_active=True)
    mainContext = mainContent(request)  
    if request.method == 'POST':
        user = request.user
        selected_room_type_id = request.POST.get('selected_room_type_id')

        try:
            mystyles = MyStyles.objects.get(user=user)
            if selected_room_type_id is not None:
                mystyles.room_type_id = selected_room_type_id
                mystyles.save()
                update_user_my_style_status(request.user)
                messages.success(request, 'Room type successfully updated.')
                return JsonResponse({'status': 'success', 'message': 'Room type successfully updated.'})
            else:
                messages.error(request, 'Invalid room type selected.')
        except MyStyles.DoesNotExist:
            if selected_room_type_id is not None:
                MyStyles.objects.create(user=user, room_type_id=selected_room_type_id)
                update_user_my_style_status(request.user)
                messages.success(request, 'Room type successfully added.')
                return JsonResponse({'status': 'success', 'message': 'Room type successfully added.'})
            else:
                messages.error(request, 'Invalid room type selected.')

    context = {
        'room_types': active_room_types, 
    }
    context.update(mainContext)
    return render(request, 'my_style/room_type_selected.html', context)


@login_required(login_url='customerauth:sign-in')
def home_type_selected(request):
    active_home_types = HomeType.objects.filter(is_active=True)
    mainContext = mainContent(request)
    if request.method == 'POST':
        user = request.user
        selected_home_type_id = request.POST.get('selected_home_type_id')

        try:
            mystyles = MyStyles.objects.get(user=user)
            if selected_home_type_id is not None:
                mystyles.home_type_id = selected_home_type_id
                mystyles.save()
                update_user_my_style_status(request.user)
                messages.success(request, 'Home type successfully updated.')
                return JsonResponse({'status': 'success', 'message': 'Room type successfully updated.'})
            else:
                messages.error(request, 'Invalid room type selected.')
        except MyStyles.DoesNotExist:
            if selected_home_type_id is not None:
                MyStyles.objects.create(user=user, home_type_id=selected_home_type_id)
                update_user_my_style_status(request.user)
                messages.success(request, 'Home type successfully added.')
                return JsonResponse({'status': 'success', 'message': 'Room type successfully added.'})
            else:
                messages.error(request, 'Invalid room type selected.')

    context = {
        'home_types': active_home_types, 
    }
    context.update(mainContext)
    return render(request, 'my_style/home_type_selected.html', context)


@login_required(login_url='customerauth:sign-in')
def home_model_selected(request):
    active_space_definations = HomeModel.objects.filter(is_active=True)
    mainContext = mainContent(request)
    if request.method == 'POST':
        user = request.user
        selected_home_model_id = request.POST.get('selected_home_model_id')

        try:
            mystyles = MyStyles.objects.get(user=user)
            if selected_home_model_id is not None:
                mystyles.home_model_id = selected_home_model_id
                mystyles.save()
                update_user_my_style_status(request.user)
                messages.success(request, 'Home type successfully updated.')
                return JsonResponse({'status': 'success', 'message': 'Home model successfully updated.'})
            else:
                messages.error(request, 'Invalid home model selected.')
        except MyStyles.DoesNotExist:
            if selected_home_model_id is not None:
                MyStyles.objects.create(user=user, home_model_id=selected_home_model_id)
                update_user_my_style_status(request.user)
                messages.success(request, 'Home type successfully added.')
                return JsonResponse({'status': 'success', 'message': 'Home model successfully added.'})
            else:
                messages.error(request, 'Invalid room type selected.')
    
    context = {
        'home_models': active_space_definations,
    }
    context.update(mainContext)
    return render(request, 'my_style/home_model_selected.html', context )


@login_required(login_url='customerauth:sign-in')
def space_definations_selected(request):
    active_space_def = SpaceDefinition.objects.filter(is_active=True)
    mainContext = mainContent(request)
    if request.method == 'POST':
        user = request.user
        selected_space_def_id = request.POST.get('selected_space_def_id')

        try:
            mystyles = MyStyles.objects.get(user=user)
            if selected_space_def_id is not None:
                mystyles.space_definition_id = selected_space_def_id
                mystyles.save()
                update_user_my_style_status(request.user)
                messages.success(request, 'Home type successfully updated.')
                return JsonResponse({'status': 'success', 'message': 'Home model successfully updated.'})
            else:
                messages.error(request, 'Invalid home model selected.')
        except MyStyles.DoesNotExist:
            if selected_space_def_id is not None:
                MyStyles.objects.create(user=user, space_definition_id=selected_space_def_id)
                update_user_my_style_status(request.user)
                messages.success(request, 'Home type successfully added.')
                return JsonResponse({'status': 'success', 'message': 'Home model successfully added.'})
            else:
                messages.error(request, 'Invalid room type selected.')
    
    context ={
        'space_defs': active_space_def, 
    }
    context.update(mainContext)
    return render(request, 'my_style/space_definations_selected.html', context)


@login_required(login_url='customerauth:sign-in')
def time_range_selected(request):
    active_time_range = TimeRange.objects.filter(is_active=True)
    mainContext = mainContent(request)
    if request.method == 'POST':
        user = request.user
        selected_time_range_id = request.POST.get('selected_time_range_id')

        try:
            mystyles = MyStyles.objects.get(user=user)
            if selected_time_range_id is not None:
                mystyles.time_range_id = selected_time_range_id
                mystyles.save()
                update_user_my_style_status(request.user)
                messages.success(request, 'Time Range successfully updated.')
                return JsonResponse({'status': 'success', 'message': 'Time Range successfully updated.'})
            else:
                messages.error(request, 'Invalid home model selected.')
        except MyStyles.DoesNotExist:
            if selected_time_range_id is not None:
                MyStyles.objects.create(user=user, time_range_id=selected_time_range_id)
                update_user_my_style_status(request.user)
                messages.success(request, 'Home type successfully added.')
                return JsonResponse({'status': 'success', 'message': 'Time Range successfully added.'})
            else:
                messages.error(request, 'Invalid room type selected.')
    context={
        'time_ranges': active_time_range
    }
    context.update(mainContext)
    return render(request, 'my_style/time_range_selected.html', context)


def update_user_my_style_status(user):
    mystyles_exists = MyStyles.objects.filter(user=user).exists()
    if mystyles_exists:
        mystyles = MyStyles.objects.get(user=user)

        if mystyles.room_type and mystyles.home_type and mystyles.home_model and mystyles.space_definition and mystyles.time_range:
            # Eğer tüm alanlar dolu ise, User modelindeki my_style alanını True yap
            User.objects.filter(pk=user.pk).update(my_style=True)

###################### My Style  Close #################



################### Forgot Passwords Open ################


def forgot_password(request):
    mainContext = mainContent(request)
    if request.method=="POST":
        un = request.POST["username"]
        pwd = request.POST["npass"]

        user = get_object_or_404(User,username=un)
        user.set_password(pwd)
        user.save()

        login(request,user)
        user_name = request.user.username 
        context1 = {
            'success_messages': f"Şifren başarıyla değiştirildi. Tekrar hoşgeldin, {user_name}!",
            'target_url':"main:home",
        }
        context1.update(mainContext)
        return render(request, "customerauth/thank-you.html", context1)
    return render(request,"customerauth/forgot_password.html",mainContext)


import random

def reset_password(request):
    username = request.GET.get("username")
    try:
        try: 
            user = get_object_or_404(User,username=username)  # Kullanıcıyı User modelinden bul
        except User.DoesNotExist:
            return JsonResponse({"status": "failed", "message":"Kullanıc Bulunamadı!"})  # Kullanıcı bulunamazsa hata döner
        otp = random.randint(100000, 999999)
        context = {
            'username': user.username,
            'otp': otp,
        }
        email_content = render_to_string('email_templates/reset_password_email.html', context)
        try:
            
            send_email_via_smtp2go([user.email], "Hesap Doğrulama", email_content)

            return JsonResponse({"status": "sent", "email": user.email, "rotp": otp})
        except:
            return JsonResponse({"status": "error", "email": user.email})
    except Exception as e:
        return JsonResponse({"status": "failed"})
    
################### Forgot Passwords Close ################



################### Wishlist Open ################
    
@login_required(login_url='customerauth:sign-in')
def wishlist_view(request):
    wishlistProducts = wishlist_model.objects.filter(user=request.user)
    title = "Beğendiklerim"
    mainContext = mainContent(request)
    context = {
        "wishlistProducts":wishlistProducts,
        "title":title,

    }
    context.update(mainContext)
    return render(request, "customerauth/wishlist.html", context)


@login_required(login_url='customerauth:sign-in')
def add_to_wishlist(request):
    messages_List = []
    
    try:
        product_id = request.GET['id']
        product = Product.objects.get(id=product_id)
        wishlist_item, created = wishlist_model.objects.get_or_create(product=product, user=request.user)
        wishlist_count = wishlist_model.objects.filter(user=request.user).count()

        if created:
            message = 'Ürün listenize eklendi!'
            tags = "success"
            messages_List.append({'message': message, 'tags': tags})
        else:
            message = 'Ürün zaten beğeni listenizde bulunuyor!'
            tags = "warning"
            messages_List.append({'message': message, 'tags': tags})

        context = {
            "status": True,
            "wishlist_count": wishlist_count,
            'messages': messages_List
        }
    except Exception as e:
        message = 'Ürün eklenirken bir sorun oluştu!'
        tags = "error"
        messages_List.append({'message': message, 'tags': tags})
        context = {
            "status": False,
            "wishlist_count": 0, 
            'messages': messages_List
        }

    message_html = render_to_string('message.html', {'messages': messages_List})
    context['message_html'] = message_html

    return JsonResponse(context)




@login_required(login_url='customerauth:sign-in')
def remove_wishlist(request):
    if request.method == "POST":
        pid = request.POST.get('id')
        
        try:
            wishlist_item = wishlist_model.objects.get(id=pid, user=request.user)
            wishlist_item.delete()
            messages.success(request, 'Ürün listenizden başarıyla kaldırıldı!')
        except wishlist_model.DoesNotExist:
            messages.error(request, 'Ürün bulunamadı veya silinemedi!')

    return redirect('customerauth:wishlist') 


################### Wishlist Close ################




@login_required(login_url='customerauth:sign-in')
def orders_List(request):
    title ="Siparişlerim"
    mainContext = mainContent(request)
    order_lists = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'order_lists': order_lists, 
        'title':title ,
    }
    context.update(mainContext)
    return render(request, 'customerauth/customer-orders.html', context)



@login_required(login_url='customerauth:sign-in')
def orders_detail(request, order_number):
    title = "Sipariş Detayları"
    mainContext = mainContent(request)
    form = CancelOrderForm()
    orders_detail = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = orders_detail.order_items.all()
    if request.method == 'POST':
        form = CancelOrderForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            orders_detail.status = 'Cancelled'
            orders_detail.order_cancel_reason = reason
            orders_detail.order_cancel_date = timezone.now()
            cancel_response = refund_payment_cancel_order(request, reason, order_number, orders_detail.id, orders_detail)
            if cancel_response:
                messages.success(request, f"{order_number} nolu siparişiniz iptal edilmiştir.")
                orders_detail.save()
                return redirect('customerauth:orders-detail', order_number=order_number)
            else:
                messages.warning(request, f"{order_number} nolu siparişiniz iptal edilirken hata oluştu.")
                return redirect('customerauth:orders-detail', order_number=order_number)
                
    
    context = {
        'orders_detail': orders_detail,
        'order_items': order_items,
        'title': title,
        "form": form
    }
    context.update(mainContext)
    return render(request, 'customerauth/order-detail.html', context)



@login_required(login_url='customerauth:sign-in')
def change_email_view(request):
    title = "Email Bilgilerim"
    mainContext = mainContent(request)
    
    if request.method == 'POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            old_email = form.cleaned_data['old_email']

            # E-posta adresini güncelle
            request.user.email = new_email
            request.user.email_verified = True  # E-posta doğrulama yapılmadı
            request.user.save()

            # Doğrulama e-postasını gönder
            #send_confirmation_email(request.user, request)

            # Eski e-posta adresine bilgilendirme gönder
            send_email_change_notification(new_email, request.user, old_email)

            messages.success(request, 'E-posta adresiniz başarıyla güncellendi.')
            return redirect('customerauth:change_email')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = {
                        'password': 'Şifre',
                        'new_email': 'Email'
                    }.get(field, field.capitalize())
                    messages.warning(request, f"{field_name}: {error}")
    else:
        form = EmailChangeForm(request.user)

    context = {
        'form': form,
        'title': title,
    }
    context.update(mainContext)

    return render(request, 'customerauth/change_email.html', context)