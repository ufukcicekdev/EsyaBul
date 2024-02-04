from django.shortcuts import redirect, render, get_object_or_404
from customerauth.forms import UserRegisterForm, ProfileForm, AddressForm,CustomPasswordChangeForm, NotificationSettingsForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from customerauth.models import User, Address, MyStyles
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from products.models import RoomType, HomeType, HomeModel, SpaceDefinition, TimeRange
from django.core.mail import EmailMessage
from django.views.decorators.http import require_POST
from actstream import action
import json
from django.contrib.auth import update_session_auth_hash


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")            
            user = authenticate(request, username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
                user_name = request.user.username 
                context1 = {
                    'success_messages': f"Tanıştığımıza memnun oldum, {user_name}!",
                    'target_url':"main:my_style_start"
                }
                action.send(request.user , verb='register')
                return render(request, "customerauth/thank-you.html", context1)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
                return redirect("customerauth:sign-in")  
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f"{field}: {error}")
            
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    
    return render(request, "customerauth/sign-up.html", context)



def login_view(request):
    if request.user.is_authenticated:
        action.send(request.user , verb='login')
        user_name = request.user.username 
        context1 = {
            'success_messages': f"Tekrar hoşgeldiniz, {user_name}!",
            'target_url':"main:my_style_start"
        }
        return render(request, "customerauth/thank-you.html", context1)
    
    if request.method == "POST":
        email_or_username = request.POST.get("email_or_username") 
        password = request.POST.get("password") 
        print("1******")
        try:
            user = User.objects.get(email=email_or_username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                return render(request, "customerauth/sign-in.html")
        user = authenticate(request, email=user.email, password=password)

        if user is not None:
            login(request, user)
            user_name = request.user.username 
            
            context1 = {
                'success_messages': f"Tekrar hoşgeldiniz, {user_name}!",
                'target_url':"main:my_style_start"
            }
            action.send(request.user , verb='login')
            return render(request, "customerauth/thank-you.html", context1)
        else:
            messages.warning(request, "Hatalı şifre veya kullanıcı adı girdiniz.")
    
    return render(request, "customerauth/sign-in.html")
        

def logout_view(request):
    action.send(request.user , verb='logout')
    logout(request)
    context1 = {
        'success_messages': "Tekrar görüşmek üzere!",
        'target_url':"main:home"
    }
    return render(request, "customerauth/thank-you.html", context1)

@login_required(login_url='customerauth:sign-in')
def profile_update(request):
    profile = get_object_or_404(User, id=request.user.id)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile Updated Successfully.")
            return redirect("customerauth:profile")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "customerauth/profile-edit.html", context)

@login_required(login_url='customerauth:sign-in')
def thank_you_view(request):
    user_name = request.user.username  # Örneğin, kullanıcı adını alıyorum

    return render(request, "customerauth/thank-you.html", {'user_name': user_name})


@login_required(login_url='customerauth:sign-in')
def customer_dashboard(request):
    user_profile = get_object_or_404(User, id=request.user.id)
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm(request.POST or None) 

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
        "form": form  
    }
    return render(request, 'customerauth/dashboard.html', context)



@login_required(login_url='customerauth:sign-in')
def password_change(request):
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
    }
    return render(request, 'customerauth/password_change.html', context)


@login_required(login_url='customerauth:sign-in')
def notifications(request):
    user_profile = get_object_or_404(User, id=request.user.id)
  # varsayılan olarak user'ın profile'ını alır, profile yoksa oluşturur

    print("user_profile",user_profile.receive_email_notifications)
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

    return render(request, 'customerauth/notifications.html', {'form': form})


@login_required(login_url='customerauth:sign-in')
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm(request.POST or None) 
    return render(request, 'customerauth/address.html', {'addresses': addresses, 'form': form })


@login_required(login_url='customerauth:sign-in')
def edit_address(request, address_id):
    # İlgili adresi getir veya 404 hatası gönder
    address = get_object_or_404(Address, id=address_id)

    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))

        print("json_data",json_data)
        username = json_data.get('username')
        last_name = json_data.get('usersurname')
        phone = json_data.get('phone')

        city_id = json_data.get('cityId')
        region_id = json_data.get('countyId')
        address_line1 = json_data.get('address_line1')
        address_name = json_data.get("title")
        address_type = json_data.get('type')

        firmName = json_data.get('corporateName')
        taxNumber = json_data.get('taxNumber')
        taxOffice = json_data.get('taxOffice')

        try:
            address.username = username
            address.usersurname = last_name
            address.phone = phone
            address.city_id = city_id
            address.region_id = region_id
            address.address_line1 = address_line1
            address.address_name = address_name
            address.address_type_id = address_type
           
            if address_type == '2':
                address.firm_name = firmName
                address.firm_taxcode = taxNumber
                address.firm_tax_home = taxOffice

            address.save()

            messages.success(request, "Address Updated Successfully.")
            return JsonResponse({"status": "success", 'redirect_url': reverse('customerauth:address-list')})
        except Exception as e:
            # Hata durumunda hatayı JSON olarak gönder
            return JsonResponse({"status": "error", "message": str(e)})

    address_data = {
        "id": address.id,
        "city": address.city_id,
        "region": address.region_id,
        "username": address.username,
        "usersurname": address.usersurname,
        "phone": address.phone,
        "address_line1": address.address_line1,
        "address_name": address.address_name,
        "firm_name": address.firm_name,
        "firm_taxcode": address.firm_taxcode,
        "firm_tax_home": address.firm_tax_home,
        "address_type_id": address.address_type_id,
    }

    return JsonResponse({'status': 'success', 'data': [address_data]})


@login_required(login_url='customerauth:sign-in')
def delete_address(request, address_id):
    print("buradsın")
    address = get_object_or_404(Address, id=address_id)
    address.delete()
    messages.success(request, "Adresiniz başarıyla silinmiştir.")
    return redirect('customerauth:address-list')


@login_required(login_url='customerauth:sign-in')
def create_address(request):
    if request.method == 'POST':
        # Gelen verilertek tek al
        json_data = json.loads(request.body.decode('utf-8'))

        username = json_data.get('username')
        last_name = json_data.get('usersurname')
        phone = json_data.get('phone')

        city_id = json_data.get('cityId')
        region_id = json_data.get('countyId')
        address_line1 = json_data.get('address_line1')
        address_name = json_data.get("title")
        address_type = json_data.get('type')

        firmName = json_data.get('corporateName')
        taxNumber = json_data.get('taxNumber')
        taxOffice = json_data.get('taxOffice')
        # Diğer gerekli alanları da alın

        try:
            new_address = Address.objects.create(
                username=username,
                usersurname=last_name,
                phone=phone,
                city_id=city_id,
                region_id  = region_id,
                address_line1=address_line1,
                address_name = address_name,
                address_type_id = address_type,
                firm_name = firmName,
                firm_taxcode = taxNumber,
                firm_tax_home = taxOffice,
                user_id=request.user.id,
            )
            messages.success(request, "Adresiniz başarıyla kayıt edilmiştir.")
            return JsonResponse({"status": "success", "message": "Address created successfully"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    else:
        # GET isteği durumunda uygun bir yanıt gönder
        return JsonResponse({"status": "error", "message": "GET isteği bekleniyor."})
    






###################### My Style  Open #################

@login_required(login_url='customerauth:sign-in')
def room_type_selected(request):
    active_room_types = RoomType.objects.filter(is_active=True)

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

    return render(request, 'my_style/room_type_selected.html', {'room_types': active_room_types})



@login_required(login_url='customerauth:sign-in')
def home_type_selected(request):
    active_home_types = HomeType.objects.filter(is_active=True)

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

    return render(request, 'my_style/home_type_selected.html', {'home_types': active_home_types})



@login_required(login_url='customerauth:sign-in')
def home_model_selected(request):
    active_space_definations = HomeModel.objects.filter(is_active=True)

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
    

    return render(request, 'my_style/home_model_selected.html', {'home_models': active_space_definations})



@login_required(login_url='customerauth:sign-in')
def space_definations_selected(request):
    active_space_def = SpaceDefinition.objects.filter(is_active=True)

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
    

    return render(request, 'my_style/space_definations_selected.html', {'space_defs': active_space_def})



@login_required(login_url='customerauth:sign-in')
def time_range_selected(request):
    active_time_range = TimeRange.objects.filter(is_active=True)

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
    

    return render(request, 'my_style/time_range_selected.html', {'time_ranges': active_time_range})





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
            'target_url':"main:home"
        }
        return render(request, "customerauth/thank-you.html", context1)
    
    return render(request,"customerauth/forgot_password.html")


import random

def reset_password(request):
    un = request.GET["username"]
    try:
        user = get_object_or_404(User,username=un)
        otp = random.randint(100000,999999)
        msz = "Merhaba {} \n{} Tek Kullanımlık Parolanız (OTP) \nBaşkalarıyla paylaşmayınız \nTeşekkürler & Saygılar \EsyaBul".format(user.username, otp)
        try:
            email = EmailMessage("Hesap Doğrulama",msz,to=[user.email])
            email.send()
            return JsonResponse({"status":"sent","email":user.email,"rotp":otp})
        except:
            return JsonResponse({"status":"error","email":user.email})
    except:
        return JsonResponse({"status":"failed"})
    
################### Forgot Passwords Close ################



################### Errors Open ################

def custom_404_page(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500_page(request):
    return render(request, 'errors/500.html', status=500)


################### Errors Close ################
