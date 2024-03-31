from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import ContactUs,SocialMedia
from django.http import JsonResponse
from products.models import Category,Product
from customerauth.models import wishlist_model

def home(request):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount = 0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        
    return render(request, 'coreBase/home.html', {'social_media_links': social_media_links, "wcount": wcount, 'main_categories':main_categories})




@login_required(login_url='customerauth:sign-in')
def my_style_start(request):
    user = request.user
    user_name = user.username
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    if user.my_style:
        return redirect('main:home')

    return render(request, 'my_style/my_style_start.html', {'user_name': user_name, "wcount":wcount})


################### Errors Open ################

def custom_404_page(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500_page(request):
    return render(request, 'errors/500.html', status=500)


################### Errors Close ################


################### Contact Open ################


def contact(request):
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    return render(request, "mainBase/contact.html", {'wcount':wcount})


def ajax_contact_form(request):
    full_name = request.GET['full_name']
    email = request.GET['email']
    phone = request.GET['phone']
    subject = request.GET['subject']
    message = request.GET['message']

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )

    data = {
        "bool": True,
        "message": "Message Sent Successfully"
    }

    return JsonResponse({"data":data})



################### Contact Close ################


def category_list(request):
    categories_with_subcategories = []
    
    for category in Category.objects.all():
        category_data = {
            'category': category,
            'subcategories': category.subcategories.all()  # Alt kategorileri al
        }
        categories_with_subcategories.append(category_data)
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    context = {
        "categories_with_subcategories":categories_with_subcategories,
        "wcount":wcount
    }
    return render(request, 'core/categories.html', context)


def category_product_list_view(request, slug):
    products = get_products_in_category(slug)

    wcount = 0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    
    context = {
        "product_category": Category.objects.all(),
        "products": products,
        "wcount": wcount
    }
    
    return render(request, "core/category-product-list.html", context)



def get_products_in_category(category_slug):
    category = Category.objects.get(slug=category_slug)
    products = category.product_set.all()  
    sub_categories = category.children.all()  

    for sub_category in sub_categories:
        products |= sub_category.product_set.all()

    return products