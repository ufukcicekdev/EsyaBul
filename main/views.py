from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import ContactUs,SocialMedia, HomeMainBanner
from django.http import JsonResponse
from products.models import Category,Product, ProductReview,Cart,CartItem
from customerauth.models import wishlist_model
from django.http import Http404
from django.db.models import Q,Avg
from products.forms import AddToCartForm

def home(request):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    homemainbanners = HomeMainBanner.objects.filter(is_active=True)
    wcount = 0
    hcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
        except Cart.DoesNotExist:
            pass

    context = {
        'social_media_links': social_media_links, 
        "wcount": wcount, 
        'main_categories':main_categories,
        "homemainbanners":homemainbanners,
        "hcount":hcount
    }
        
    return render(request, 'coreBase/home.html', context)




@login_required(login_url='customerauth:sign-in')
def my_style_start(request):
    user = request.user
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount=0
    hcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
        except Cart.DoesNotExist:
            pass
    user_name = user.username
    
    if user.my_style:
        return redirect('main:home')

    return render(request, 'my_style/my_style_start.html', {'user_name': user_name, 
                    "wcount":wcount, "main_categories":main_categories,"social_media_links":social_media_links,"hcount":hcount})


################### Errors Open ################

def custom_404_page(request, exception):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount=0
    hcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
        except Cart.DoesNotExist:
            pass
    context = {
        "social_media_links":social_media_links,
        "main_categories":main_categories,
        "wcount":wcount,
        "hcount":hcount
    }
    return render(request, 'errors/404.html', context, status=404)

def custom_500_page(request):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount=0
    hcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
        except Cart.DoesNotExist:
            pass
    context = {
        "social_media_links":social_media_links,
        "main_categories":main_categories,
        "wcount":wcount,
        "hcount":hcount
    }
    return render(request, 'errors/500.html', context, status=500)


################### Errors Close ################


################### Contact Open ################


def contact(request):
    social_media_links = SocialMedia.objects.all()
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    wcount=0
    hcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
        except Cart.DoesNotExist:
            pass
    return render(request, "mainBase/contact.html", {'wcount':wcount, 'main_categories':main_categories, 
                                                     'social_media_links':social_media_links,"hcount":hcount})


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
    social_media_links = SocialMedia.objects.all()
    category_slug_list = category_slugs.split('/')
    wcount=0 
    hcount=0   
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
        try:
            handbag = Cart.objects.get(user=request.user, order_completed=False)
            hcount = CartItem.objects.filter(cart=handbag).count()
        except Cart.DoesNotExist:
            pass

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
            "hcount":hcount,
            "social_media_links":social_media_links,
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
        "hcount":hcount,
        "category": main_category,
        "category_name": target_category,
        "subcategories": subcategories,
        "main_categories": main_categories,
        "social_media_links":social_media_links,
    }
    
    return render(request, "core/category-product-list.html", context)


