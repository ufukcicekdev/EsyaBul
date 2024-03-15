from django.shortcuts import redirect, render, get_object_or_404
from customerauth.forms import UserRegisterForm, ProfileForm, AddressForm,CustomPasswordChangeForm, NotificationSettingsForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from customerauth.models import User, Address, MyStyles, wishlist_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from products.models import RoomType, HomeType, HomeModel, SpaceDefinition, TimeRange, Product
from django.core.mail import EmailMessage
from actstream import action
import json
from django.contrib.auth import update_session_auth_hash
from django.core import serializers
from django.template.loader import render_to_string
from cities_light.models import Country, City, Region, SubRegion
from main.models import SocialMedia

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
        try:
            user = User.objects.get(email=email_or_username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                messages.warning(request, "Hatalı şifre veya kullanıcı adı girdiniz.")
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
    title = "Hesabım"
    profile = get_object_or_404(User, id=request.user.id)
    wcount =0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
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
        "title":title,
        "wcount":wcount
    }

    return render(request, "customerauth/profile-edit.html", context)

@login_required(login_url='customerauth:sign-in')
def thank_you_view(request):
    user_name = request.user.username  # Örneğin, kullanıcı adını alıyorum
    wcount =0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    return render(request, "customerauth/thank-you.html", {'user_name': user_name, "wcount":wcount})


@login_required(login_url='customerauth:sign-in')
def customer_dashboard(request):
    user_profile = get_object_or_404(User, id=request.user.id)
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm(request.POST or None) 
    title ="Hesabım"
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
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
        "wcount":wcount
    }
    return render(request, 'customerauth/dashboard.html', context)


@login_required(login_url='customerauth:sign-in')
def password_change(request):
    title = "Hesabım"
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
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
        "wcount":wcount
    }
    return render(request, 'customerauth/password_change.html', context)


@login_required(login_url='customerauth:sign-in')
def notifications(request):
    title="Bildirimlerim"
    user_profile = get_object_or_404(User, id=request.user.id)
  # varsayılan olarak user'ın profile'ını alır, profile yoksa oluşturur
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()

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

    return render(request, 'customerauth/notifications.html', {'form': form, 'title':title, "wcount":wcount})

###################### Address  Open #################

@login_required(login_url='customerauth:sign-in')
def address_list(request):
    title ="Adreslerim"
    wcount =0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm(request.POST or None) 
    return render(request, 'customerauth/address.html', {'addresses': addresses, 'form': form, 'title':title ,"wcount":wcount})


@login_required(login_url='customerauth:sign-in')
def create_address(request):
    title ="Adreslerim"
    wcount =0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()
            messages.success(request,"Adresiniz Başarıyla Eklenmiştir.")
            return redirect('customerauth:address-list')  # Başarıyla eklendiğinde yönlendirilecek sayfa
        else:
            print("form error: ", form.errors)
    else:
        form = AddressForm()

    return render(request, 'customerauth/add-new-address.html', {'form': form, 'title': title, "wcount":wcount})


@login_required(login_url='customerauth:sign-in')
def edit_address(request, address_id):
    title ="Adreslerim"
    address = get_object_or_404(Address, id=address_id)
    wcount =0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request,"Adresiniz Başarıyla Güncellenmiştir.")
            return redirect('customerauth:address-list')
    else:
        form = AddressForm(instance=address)

    return render(request, 'customerauth/edit-address.html', {'form': form, 'address': address, 'title': title, "wcount":wcount})


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
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
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

    return render(request, 'my_style/room_type_selected.html', {'room_types': active_room_types, "wcount":wcount})


@login_required(login_url='customerauth:sign-in')
def home_type_selected(request):
    active_home_types = HomeType.objects.filter(is_active=True)
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
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

    return render(request, 'my_style/home_type_selected.html', {'home_types': active_home_types, "wcount":wcount})


@login_required(login_url='customerauth:sign-in')
def home_model_selected(request):
    active_space_definations = HomeModel.objects.filter(is_active=True)
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
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
    

    return render(request, 'my_style/home_model_selected.html', {'home_models': active_space_definations, "wcount":wcount})


@login_required(login_url='customerauth:sign-in')
def space_definations_selected(request):
    active_space_def = SpaceDefinition.objects.filter(is_active=True)
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
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
    

    return render(request, 'my_style/space_definations_selected.html', {'space_defs': active_space_def, "wcount":wcount})


@login_required(login_url='customerauth:sign-in')
def time_range_selected(request):
    active_time_range = TimeRange.objects.filter(is_active=True)
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
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
    

    return render(request, 'my_style/time_range_selected.html', {'time_ranges': active_time_range, "wcount":wcount})


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
    username = request.GET.get("username")
    try:
        user = get_object_or_404(User, username=username)
        otp = random.randint(100000, 999999)
        social_media_links = SocialMedia.objects.all()
        context = {
            'username': user.username,
            'otp': otp,
            "social_media_links":social_media_links
        }
        email_content = render_to_string('email_templates/reset_password_email.html', context)
        try:
            email = EmailMessage("Hesap Doğrulama", email_content, to=[user.email])
            email.content_subtype = 'html' 
            email.send()
            return JsonResponse({"status": "sent", "email": user.email, "rotp": otp})
        except:
            return JsonResponse({"status": "error", "email": user.email})
    except:
        return JsonResponse({"status": "failed"})
    
################### Forgot Passwords Close ################



################### Wishlist Open ################
    
@login_required(login_url='customerauth:sign-in')
def wishlist_view(request):
    wishlistProducts = wishlist_model.objects.filter(user=request.user)
    title = "Beğendiklerim"
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    context = {
        "wishlistProducts":wishlistProducts,
        "title":title,
        "wcount":wcount
    }
    return render(request, "customerauth/wishlist.html", context)

@login_required(login_url='customerauth:sign-in')
def add_to_wishlist(request):
    product_id = request.GET['id']
    product = Product.objects.get(id=product_id)
    context = {}
    wishlist_count = wishlist_model.objects.filter(product=product, user=request.user).count()
    
    if wishlist_count > 0:
        wishlist_count = wishlist_model.objects.filter(user=request.user).count()
        context = {
            "bool": True,
            "wishlist_count":wishlist_count
        }
    else:
        new_wishlist = wishlist_model.objects.create(
            user=request.user,
            product=product,
        )
        wishlist_count = wishlist_model.objects.filter(user=request.user).count()
        context = {
            "bool": True,
            "wishlist_count":wishlist_count
        }
    return JsonResponse(context)

@login_required(login_url='customerauth:sign-in')
def remove_wishlist(request):
    pid = request.GET['id']
    wishlist = wishlist_model.objects.filter(user=request.user)
    wishlist_d = wishlist_model.objects.get(id=pid)
    delete_product = wishlist_d.delete()
    
    context = {
        "bool":True,
        "w":wishlist
    }
    wishlist_json = serializers.serialize('json', wishlist)
    t = render_to_string('customerauth/wishlist-list.html', context)
    return JsonResponse({'data':t,'w':wishlist_json})


################### Wishlist Close ################


