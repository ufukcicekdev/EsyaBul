from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import HomeMainBanner, HomeSubBanner, TeamMembers, HomePageBannerItem, Subscription
from products.models import Category,Product, ProductReview,ProductImage
from customerauth.models import wishlist_model,UserProductView
from products.models import Brand,ProductRentalPrice
from django.db.models import Q,Avg,Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ProductSearchForm,ContactForm
from .mainContent import mainContent
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from slack_send_messages.send_messages import send_contact_message
from django.db.models import Exists, OuterRef


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

def get_home_retail_products():
    key = 'get_home_retail_products'
    products = cache.get(key)
    if not products:
        best_seller_products = Product.objects.filter(is_active=True,best_seller=True).annotate(has_rental_price=Exists(ProductRentalPrice.objects.filter(product=OuterRef('pk')))).filter(has_rental_price=True).prefetch_related('related_products', 'related_products_price')[:4]
        featured_products = Product.objects.filter(is_active=True,is_featured=True).annotate(has_rental_price=Exists(ProductRentalPrice.objects.filter(product=OuterRef('pk')))).filter(has_rental_price=True).prefetch_related('related_products', 'related_products_price')[:4]
        latest_products = Product.objects.filter(is_active=True).annotate(has_rental_price=Exists(ProductRentalPrice.objects.filter(product=OuterRef('pk')))).filter(has_rental_price=True).order_by('-created_at').prefetch_related('related_products', 'related_products_price')[:4]
    
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
    retails_products = get_home_retail_products()
    #sales_products = get_home_sales_products()

    banners = HomePageBannerItem.objects.filter(position__in=['left', 'right']).order_by('id')
    sliders = HomePageBannerItem.objects.filter(position='slider').order_by('id')

    context = {
        "homemainbanners": homemainbanners,
        "homesubbanners": homesubbanners,
        "best_seller_products": product_data['best_seller_products'],
        "featured_products": product_data['featured_products'],
        "latest_products": product_data['latest_products'],
        "banners": banners,
        "sliders": sliders,
        "brand_data":brand_data,
        "retails_products":retails_products,
        "description": "Esyala.com, mobilya, ev dekorasyonu ve elektronik ürünler sunan online alışveriş platformudur. Evinizi kolayca yenileyin!"
    }

    if request.user.is_authenticated:
        user_product_view = UserProductView.objects.filter(user=request.user).order_by('-created_at')[:10]
        context.update({'user_product_view': user_product_view})

    context.update(mainContext)
    
    return render(request, 'coreBase/home.html', context)



@login_required(login_url='customerauth:sign-in')
def my_style_start(request):
    address_type = request.GET.get('my_style_type')
    user = request.user
    user_name = user.username
    mainContext = mainContent(request)
    if user.my_style and address_type!='new':
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
    description = "Esyala.com ile iletişime geçin! Sorularınız, geri bildirimleriniz veya destek talepleriniz için bize ulaşın. Müşteri memnuniyeti ve çözüm odaklı hizmet anlayışımızla, sizlere en iyi deneyimi sunmak için buradayız."
    mainContext["description"] = description

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_instance = form.save()  # Formu kaydediyoruz

            # Slack'e mesaj gönder
            contact_data = {
                'full_name': contact_instance.full_name,
                'email': contact_instance.email,
                'phone': contact_instance.phone,
                'subject': contact_instance.subject,
                'message': contact_instance.message,
            }
            send_contact_message(contact_data)  # Slack fonksiyonunu burada çağırıyoruz

            messages.success(request, 'Mesajınız başarıyla gönderildi!')
            return redirect('main:contact')  
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurduğunuzdan emin olun.')
            mainContext['form'] = form
    else:
        mainContext['form'] = ContactForm()

    return render(request, "mainBase/contact.html", mainContext)


@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def about(request):
    mainContext = mainContent(request)
    teams_Members = TeamMembers.objects.filter(is_active=True).order_by("id")

    sorted_members = {}
    for member in teams_Members:
        level = member.level  
        if level not in sorted_members:
            sorted_members[level] = []
        sorted_members[level].append(member)


    context = {
        "teamsMembers": teams_Members,
        "sorted_members": sorted_members,  
    }
    context.update(mainContext)
    description = "Esyala.com hakkında bilgi edinin. Kaliteli hizmet ve müşteri memnuniyeti için buradayız. Misyonumuz, vizyonumuz ve değerlerimiz hakkında daha fazla bilgi alın."
    context["description"] = description
    return render(request, "mainBase/about.html", context)



@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def faqs(request):
    mainContext = mainContent(request)
    description = "Esyala.com Sık Sorulan Sorular (SSS) sayfası, hizmetlerimiz, hesap yönetimi ve diğer konular hakkında en çok merak edilen sorulara yanıt sunar. Hızlı çözümler için doğru yerdesiniz!"
    mainContext["description"] = description
    return render(request, "mainBase/faq.html", mainContext)
@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def does_it_work(request):
    mainContext = mainContent(request)
    description = "Esyala.com'un nasıl çalıştığını öğrenin. Kullanıcı dostu ara yüzümüzle işlerinizi kolaylaştırın ve etkili sonuçlar elde edin."
    mainContext["description"] = description
    return render(request, "mainBase/doesitwork.html", mainContext)








################ Contact Close ################
@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def dynamic_category_product_list_view(request, category_slugs):
    category_slug_list = category_slugs.split('/')
    mainContext = mainContent(request)

    main_category = get_object_or_404(Category, slug=category_slug_list[0])
    subcategories = main_category.children.all()

    if len(category_slug_list) == 1:
        target_category = main_category
        category_query = Q(category__in=main_category.children.all())
    else:
        target_category = get_object_or_404(Category, slug=category_slug_list[-1])
        category_query = Q(category=target_category)

    # Ürünleri ve ilişkili verileri daha verimli getirin
    products = Product.objects.filter(category_query, is_active=True).select_related('category').prefetch_related(
        Prefetch('related_products', queryset=ProductImage.objects.all()),
        Prefetch('reviews', queryset=ProductReview.objects.all()),
        Prefetch('wishes', queryset=wishlist_model.objects.all())
    ).annotate(average_rating=Avg('reviews__rating')).order_by('id')

    for subcategory in subcategories:
        subcategory.product_count = Product.objects.filter(category=subcategory, is_active=True).count()

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')

    try:
        page_products = paginator.page(page_number)
    except PageNotAnInteger:
        page_products = paginator.page(1)
    except EmptyPage:
        page_products = paginator.page(paginator.num_pages)

    category_image = target_category.image.url if target_category.image else 'https://filestorages.fra1.cdn.digitaloceanspaces.com/esyabul/Site-Images/naomi-hebert-2dcYhvbHV-M-unsplash.jpg'

    context = {
        "tumrunler": False,
        "products": page_products,
        "product_count": products.count(),
        "category": main_category,
        "category_name": target_category,
        "subcategories": subcategories,
        "main_slug": main_category,
        "image": category_image,  # Resmi context'e ekliyoruz
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
        products = Product.objects.filter(Q(is_active=True) &
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
        "description": "Esyala.com, mobilya, ev dekorasyonu ve elektronik ürünlerle kiralama ve satın alma seçenekleri sunan geniş yelpazeli online alışveriş platformudur."
    }
    context.update(mainContext)
    return render(request, 'core/search_results.html', context)





def get_main_category_products(request, mainContext, category_slug_list):
    main_category = get_object_or_404(Category, slug=category_slug_list[0])
    main_slug=main_category
    products = Product.objects.filter(is_active=True).order_by("id")
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



@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def rental_product_list_view(request):
    mainContext = mainContent(request)

    # Kiralama fiyatı olan ürünleri al
    products = Product.objects.filter(
        is_active=True
    ).annotate(
        has_rental_price=Exists(ProductRentalPrice.objects.filter(product=OuterRef('pk')))
    ).filter(
        has_rental_price=True  # Sadece kiralama fiyatı olan ürünleri seçiyoruz
    ).select_related('category').prefetch_related(
        Prefetch('related_products', queryset=ProductImage.objects.all()),
        Prefetch('reviews', queryset=ProductReview.objects.all()),
        Prefetch('wishes', queryset=wishlist_model.objects.all())
    ).annotate(average_rating=Avg('reviews__rating')).order_by('id')

    # Kiralama fiyatı olan ürünlerin kategorilerini ve alt kategorilerini al
    categories = set(product.category for product in products)
    subcategories = {category: category.children.all() for category in categories}

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')

    try:
        page_products = paginator.page(page_number)
    except PageNotAnInteger:
        page_products = paginator.page(1)
    except EmptyPage:
        page_products = paginator.page(paginator.num_pages)

    # Kategoriler için resim veya varsayılan bir resim al
    category_images = {
        category.id: category.image.url if category.image else 'https://filestorages.fra1.cdn.digitaloceanspaces.com/esyabul/Site-Images/naomi-hebert-2dcYhvbHV-M-unsplash.jpg'
        for category in categories
    }

    context = {
        "tumrunler": False,
        "products": page_products,
        "product_count": products.count(),
        "categories": categories,  # Kiralama fiyatı olan ürünlerin kategorileri
        "subcategories": subcategories,  # Kiralama fiyatı olan ürünlerin alt kategorileri
        "category_images": category_images,  # Kategorilerin resimleri
    }
    context.update(mainContext)

    return render(request, "core/retail_category_product_list.html", context)




@cache_page(60 * 60 * 6)  # 6 saatlik cache
@vary_on_cookie
def sales_product_list_view(request):
    mainContext = mainContent(request)

    # Kiralama fiyatı olan ürünleri al
    products = Product.objects.filter(
        is_active=True
    ).select_related('category').prefetch_related(
        Prefetch('related_products', queryset=ProductImage.objects.all()),
        Prefetch('reviews', queryset=ProductReview.objects.all()),
        Prefetch('wishes', queryset=wishlist_model.objects.all())
    ).annotate(average_rating=Avg('reviews__rating')).order_by('id')

    # Kiralama fiyatı olan ürünlerin kategorilerini ve alt kategorilerini al
    categories = set(product.category for product in products)
    subcategories = {category: category.children.all() for category in categories}

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')

    try:
        page_products = paginator.page(page_number)
    except PageNotAnInteger:
        page_products = paginator.page(1)
    except EmptyPage:
        page_products = paginator.page(paginator.num_pages)

    # Kategoriler için resim veya varsayılan bir resim al
    category_images = {
        category.id: category.image.url if category.image else 'https://filestorages.fra1.cdn.digitaloceanspaces.com/esyabul/Site-Images/naomi-hebert-2dcYhvbHV-M-unsplash.jpg'
        for category in categories
    }

    context = {
        "tumrunler": False,
        "products": page_products,
        "product_count": products.count(),
        "categories": categories,  # Kiralama fiyatı olan ürünlerin kategorileri
        "subcategories": subcategories,  # Kiralama fiyatı olan ürünlerin alt kategorileri
        "category_images": category_images,  # Kategorilerin resimleri
    }
    context.update(mainContext)

    return render(request, "core/sales_category_product_list.html", context)