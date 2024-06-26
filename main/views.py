from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import ContactUs,SocialMedia, HomeMainBanner, HomeSubBanner, TeamMembers
from django.http import JsonResponse
from products.models import Category,Product, ProductReview,Cart,CartItem
from customerauth.models import wishlist_model
from django.http import Http404
from django.db.models import Q,Avg,Prefetch
from products.forms import AddToCartForm
import random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ProductSearchForm
from .mainContent import mainContent
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
import random
from django.views.decorators.vary import vary_on_cookie

@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def home(request):
    homemainbanners = HomeMainBanner.objects.filter(is_active=True)
    homesubbanners = HomeSubBanner.objects.filter(is_active=True)
    products_queryset = Product.objects.filter(is_active=True)
    best_seller_products = products_queryset.filter(best_seller=True).order_by('?')[:16]
    featured_products = products_queryset.filter(is_featured=True).order_by('?')[:16]
    latest_products = list(products_queryset.order_by('-created_at')[:30])
    random.shuffle(latest_products)
    latest_products = latest_products[:16]
    
    mainContext = mainContent(request)
    context = {
        "homemainbanners": homemainbanners,
        "best_seller_products": best_seller_products,
        "featured_products": featured_products,
        "latest_products": latest_products,
        "best_products": best_seller_products, 
        "homesubbanners": homesubbanners,
    }

    context.update(mainContext)
    
    return render(request, 'coreBase/home.html', context)




@login_required(login_url='customerauth:sign-in')
def my_style_start(request):
    user = request.user
    user_name = user.username
    mainContext = mainContent(request)
    if user.my_style:
        return redirect('main:home')
    
    context ={
        'user_name': user_name,  
    }
    context.update(mainContext)
    return render(request, 'my_style/my_style_start.html', )


################### Errors Open ################

def custom_404_page(request, exception):
    mainContext = mainContent(request)
    return render(request, 'errors/404.html', mainContext, status=404)

def custom_500_page(request):
    mainContext = mainContent(request)
    return render(request, 'errors/500.html', mainContext, status=500)


################### Errors Close ################


################### Contact Open ################

@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def contact(request):
    mainContext = mainContent(request)
    return render(request, "mainBase/contact.html", mainContext)
@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def about(request):
    mainContext = mainContent(request)
    teamsMembers = TeamMembers.objects.filter(is_active=True).order_by("id")
    context = {
        "teamsMembers":teamsMembers,
    }
    context.update(mainContext)
    return render(request, "mainBase/about.html", context)
@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def faqs(request):
    mainContext = mainContent(request)
    return render(request, "mainBase/faq.html", mainContext)
@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def does_it_work(request):
    mainContext = mainContent(request)
    return render(request, "mainBase/doesitwork.html", mainContext)




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

    messages_List = []
    message = 'Başarılı bir şekilde gönderildi!'
    tags = "success"
    messages_List.append({'message': message, 'tags': tags})
    message_html = render_to_string('message.html', {'messages': messages_List})

    context = {
        "status": True,
        "messages": messages_List,
        "message_html": message_html,
    }


    return JsonResponse(context)



################ Contact Close ################
@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def dynamic_category_product_list_view(request, category_slugs):
    category_slug_list = category_slugs.split('/')
    mainContext = mainContent(request)

    if category_slugs == "tum-urunler":
        context = get_main_category_products(request, mainContext, category_slug_list)
    else:
        main_category = get_object_or_404(Category, slug=category_slug_list[0])
        subcategories = main_category.children.all()

        if len(category_slug_list) == 1:
            target_category = main_category
            category_query = Q(category__in=main_category.children.all())
        else:
            target_category = get_object_or_404(Category, slug=category_slug_list[-1])
            category_query = Q(category=target_category)

        # Ürünleri ve ilişkili verileri daha verimli getirin
        products = Product.objects.filter(category_query).select_related('category').prefetch_related(
            Prefetch('reviews', queryset=ProductReview.objects.all()),
            Prefetch('wishes', queryset=wishlist_model.objects.all())
        ).annotate(average_rating=Avg('reviews__rating')).order_by('id')

        for subcategory in subcategories:
            subcategory.product_count = Product.objects.filter(category=subcategory).count()

        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')

        try:
            page_products = paginator.page(page_number)
        except PageNotAnInteger:
            page_products = paginator.page(1)
        except EmptyPage:
            page_products = paginator.page(paginator.num_pages)

        context = {
            "tumrunler": False,
            "products": page_products,
            "product_count": products.count(),
            "category": main_category,
            "category_name": target_category,
            "subcategories": subcategories,
            "main_slug": main_category,
        }
        context.update(mainContext)

    return render(request, "core/category-product-list.html", context)


def search_view(request):
    mainContext = mainContent(request)

    search_form = ProductSearchForm(request.GET)
    products = []

    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(information__icontains=query)
        ).order_by('id')

    paginator = Paginator(products, 12)  
    page_number = request.GET.get('page')
    try:
        page_products = paginator.page(page_number)
    except PageNotAnInteger:
        page_products = paginator.page(1)  
    except EmptyPage:
        page_products = paginator.page(paginator.num_pages)

    context = {
        'search_form': search_form, 
        'products': page_products,
        "product_count": products.count(),
    }
    context.update(mainContext)
    return render(request, 'core/search_results.html', context)



@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def get_main_category_products(request, mainContext, category_slug_list):
    main_category = get_object_or_404(Category, slug=category_slug_list[0])
    main_slug=main_category
    products = Product.objects.all().order_by("id")
    paginator = Paginator(products, 12)  
    page_number = request.GET.get('page')
    try:
        page_products = paginator.page(page_number)
    except PageNotAnInteger:
        page_products = paginator.page(1)  
    except EmptyPage:
        page_products = paginator.page(paginator.num_pages)
    context = {
        "tumrunler":True,
        "products": page_products,
        "product_count":products.count(),
        "category_name": main_category,
        "all_categories": Category.objects.all(),
        "main_slug":main_slug
    }
    context.update(mainContext)
    return context