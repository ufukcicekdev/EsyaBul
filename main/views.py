from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import ContactUs,SocialMedia
from django.http import JsonResponse
from products.models import Category,Product

def home(request):
    social_media_links = SocialMedia.objects.all()
    return render(request, 'core/home.html', {'social_media_links': social_media_links})


@login_required(login_url='customerauth:sign-in')
def my_style_start(request):
    user = request.user
    user_name = user.username
    print("********************************",user.my_style)
    if user.my_style:
        return redirect('main:home')

    return render(request, 'my_style/my_style_start.html', {'user_name': user_name})


################### Errors Open ################

def custom_404_page(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500_page(request):
    return render(request, 'errors/500.html', status=500)


################### Errors Close ################


################### Contact Open ################


def contact(request):
    return render(request, "main/contact.html")


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
    categories = Category.objects.filter(is_active=True)

    context = {
        "categories":categories
    }
    return render(request, 'core/categories.html', context)


def category_product_list__view(request, slug):
    print("buradasiiii*****")
    category = Category.objects.get(slug=slug) # food, Cosmetics
    products = Product.objects.filter(is_active=True, category=category)

    context = {
        "category":category,
        "products":products,
    }
    return render(request, "core/category-product-list.html", context)