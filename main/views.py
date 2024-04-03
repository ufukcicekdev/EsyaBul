from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import ContactUs,SocialMedia
from django.http import JsonResponse
from products.models import Category,Product, ProductReview
from customerauth.models import wishlist_model
from django.http import Http404
from django.db.models import Q,Avg


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
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    user_name = user.username
    
    if user.my_style:
        return redirect('main:home')

    return render(request, 'my_style/my_style_start.html', {'user_name': user_name, "wcount":wcount, "main_categories":main_categories})


################### Errors Open ################

def custom_404_page(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500_page(request):
    return render(request, 'errors/500.html', status=500)


################### Errors Close ################


################### Contact Open ################


def contact(request):
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    return render(request, "mainBase/contact.html", {'wcount':wcount, 'main_categories':main_categories})


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

def dynamic_category_product_list_view(request, category_slugs):
    category_slug_list = category_slugs.split('/')
    
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()

    # Ana kategorileri al
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    
    # Eğer category_slugs "tum-urunler" ise, tüm ürünleri getir
    if category_slugs == "tum-urunler":
        main_category = get_object_or_404(Category, slug=category_slug_list[0])
        products = Product.objects.all()
        context = {
            "products": products,
            "main_categories1": main_categories,
            "category_name": main_category,
            "wcount":wcount,
            "all_categories": Category.objects.all()  # Tüm kategorileri döndür
        }
        return render(request, "core/category-product-list.html", context)
    
    # Eğer category_slugs bir kategoriye aitse, ilgili ürünleri getir
    main_category = get_object_or_404(Category, slug=category_slug_list[0])
    subcategories = main_category.children.all()
    if len(category_slug_list) == 1:
        target_category = main_category
    else:
        target_category = get_object_or_404(Category, slug=category_slug_list[-1])
    if len(category_slug_list) == 1: 
        getMainCategoryList = main_category.children.all()
        category_query = Q()

        for category in getMainCategoryList:
            category_query |= Q(category=category)

        products = Product.objects.filter(category_query)

    else:
        products = Product.objects.filter(category=target_category)
        
    for subcategory in subcategories:
        subcategory.product_count = Product.objects.filter(category=subcategory).count()
    
    
    for product in products:
        product.reviews.set(ProductReview.objects.filter(product=product))
        product.wishes.set(wishlist_model.objects.filter(product=product))
        product.average_rating = int(product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0)


    context = {
        "products": products,
        "wcount": wcount,
        "category": main_category,
        "category_name": target_category,
        "subcategories": subcategories,
        "main_categories": main_categories,
    }
    
    return render(request, "core/category-product-list.html", context)


