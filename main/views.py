from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import SocialMedia, HomeMainBanner, HomeSubBanner, TeamMembers, HomePageBannerItem,ContactUs, Subscription
from django.http import JsonResponse
from products.models import Category,Product, ProductReview,Cart,CartItem,ProductImage
from customerauth.models import wishlist_model,UserProductView
from products.models import Brand
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
from django.core.cache import cache



def get_home_main_banners():
    key = 'home_main_banners'
    banners = cache.get(key)
    if not banners:
        banners = list(HomeMainBanner.objects.filter(is_active=True))
        cache.set(key, banners, 60 * 60 * 6)  # 6 saat cache
    return banners

def get_home_sub_banners():
    key = 'home_sub_banners'
    banners = cache.get(key)
    if not banners:
        banners = list(HomeSubBanner.objects.filter(is_active=True))
        cache.set(key, banners, 60 * 60 * 6)  # 6 saat cache
    return banners



def get_homepage_products():
    key = 'homepage_products'
    products = cache.get(key)
    
    if not products:
        # Tüm ürünleri ve ilgili ürün görsellerini prefetch_related ile önceden çekiyoruz
        best_seller_products = Product.objects.filter(is_active=True, best_seller=True).prefetch_related('related_products')[:16]
        featured_products = Product.objects.filter(is_active=True, is_featured=True).prefetch_related('related_products')[:16]
        latest_products = Product.objects.filter(is_active=True).order_by('-created_at').prefetch_related('related_products')[:16]
        
        products = {
            'best_seller_products': list(best_seller_products),
            'featured_products': list(featured_products),
            'latest_products': list(latest_products),
        }
        
        cache.set(key, products, 60 * 60 * 6)  # 6 saat cache süresi
    
    return products


def get_homepage_brand():
    key = 'homepage_brand'
    brands = cache.get(key)  # Burada 'brands' olarak güncelledik
    if not brands:  # Eğer cache'te yoksa, DB'den al ve cache'e kaydet
        brands = list(Brand.objects.filter(is_active=True))
        cache.set(key, brands, 60 * 60 * 6) 
    return brands

@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def home(request):
    mainContext = mainContent(request)
    homemainbanners = get_home_main_banners()
    homesubbanners = get_home_sub_banners()
    product_data = get_homepage_products()
    brand_data = get_homepage_brand()

    description = "Esyala.com, mobilya, ev dekorasyonu, elektronik ve daha fazlasını kapsayan geniş ürün yelpazesiyle online alışveriş platformudur. Kiralama ve satın alma seçenekleriyle evinizi yenilemek artık çok daha kolay!"
    banners = HomePageBannerItem.objects.filter(position__in=['left', 'right']).order_by('order')
    sliders = HomePageBannerItem.objects.filter(position='slider').order_by('order')

    context = {
        "homemainbanners": homemainbanners,
        "homesubbanners": homesubbanners,
        "best_seller_products": product_data['best_seller_products'],
        "featured_products": product_data['featured_products'],
        "latest_products": product_data['latest_products'],
        "banners": banners,
        "sliders": sliders,
        "description":description,
        "brand_data":brand_data
    }

    if request.user.is_authenticated:
        user_product_view = UserProductView.objects.filter(user=request.user).order_by('-created_at')[:10]
        context.update({'user_product_view': user_product_view})

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
    return render(request, 'my_style/my_style_start.html', context)


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
    description = "Eşyala.com ile iletişime geçin! Sorularınız, geri bildirimleriniz veya destek talepleriniz için bize ulaşın. Müşteri memnuniyeti ve çözüm odaklı hizmet anlayışımızla, sizlere en iyi deneyimi sunmak için buradayız."
    mainContext["description"] = description
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
    description = "Eşyala.com hakkında daha fazla bilgi edinin. Biz kimiz, ne yapıyoruz ve neden bu kadar tutkuluyuz? Eşyala.com, size kaliteli hizmet sunmak ve ihtiyaçlarınıza en iyi şekilde cevap vermek için burada. Misyonumuz, vizyonumuz ve değerlerimizle ilgili detaylar için sayfamızı ziyaret edin."
    context["description"] = description
    return render(request, "mainBase/about.html", context)
@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def faqs(request):
    mainContext = mainContent(request)
    description = "Eşyala.com Sık Sorulan Sorular (SSS) sayfası, kullanıcılarımızın en çok merak ettiği soruları yanıtlamaktadır. Hizmetlerimiz, kullanımı, hesap yönetimi ve diğer konularla ilgili kapsamlı cevaplar bulabilirsiniz. Sorularınıza hızlı ve etkili çözümler arıyorsanız, doğru yerdesiniz."
    mainContext["description"] = description
    return render(request, "mainBase/faq.html", mainContext)
@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def does_it_work(request):
    mainContext = mainContent(request)
    description = "Eşyala.com'un nasıl çalıştığını öğrenin. Kullanıcı dostu ara yüzümüzle işlerinizi kolaylaştırın ve etkili sonuçlar elde edin."
    mainContext["description"] = description
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

    # if category_slugs == "tum-urunler":
    #     context = get_main_category_products(request, mainContext, category_slug_list)
    #     print(context)
    # else:
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
    Prefetch('related_products', queryset=ProductImage.objects.all()),
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


def get_search_category():
    key = 'category'
    category = cache.get(key)
    if not category:
        category = list(Category.objects.filter(parent=None, is_active=True))
        cache.set(key, category, 60 * 60 * 6)  # 6 saat cache
    return category



def search_view(request):
    mainContext = mainContent(request)
    search_category = get_search_category()
    search_form = ProductSearchForm(request.GET)
    products = Product.objects.none()  # Başlangıçta boş bir QuerySet

    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        request.session['search_query'] = query  # Sorguyu oturumda saklayın
    else:
        query = request.session.get('search_query', '')  # Oturumdan sorguyu alın

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(information__icontains=query)
        ).order_by('id')

    paginator = Paginator(products, 12)  
    page_number = request.GET.get('page', 1)  # Varsayılan olarak 1. sayfa
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
        "search_category": search_category,
        "description": "Esyala.com, mobilya, ev dekorasyonu, elektronik ve daha fazlasını kapsayan geniş ürün yelpazesiyle online alışveriş platformudur. Kiralama ve satın alma seçenekleriyle evinizi yenilemek artık çok daha kolay!"
    }
    context.update(mainContext)
    return render(request, 'core/search_results.html', context)





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




def subscribe(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if email:
            subscription, created = Subscription.objects.get_or_create(email=email)
            if created:
                messages.success(request, "Abonelik işlemi başarıyla tamamlandı.")
            else:
                messages.info(request, "Bu e-posta adresi zaten kayıtlı.")
        return redirect('main:home') 
    return render(request, 'coreBase/home.html')
