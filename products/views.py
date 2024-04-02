from django.shortcuts import render,redirect,get_object_or_404
from .models import Product, Category, ProductReview
from customerauth.models import wishlist_model
from products.forms import ProductReviewForm
from django.urls import reverse
from django.db.models import Avg


def product_detail_view(request, product_slug):
    main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    wcount=0
    if request.user.is_authenticated:
        wcount = wishlist_model.objects.filter(user=request.user).count()
    
    reviews = ProductReview.objects.filter(product=product)
    wishCount = wishlist_model.objects.filter(product=product)
    if wishCount.exists():
        wish_count = wishCount.count()
    else:
        wish_count = 0

    average_rating = int(reviews.aggregate(Avg('rating'))['rating__avg'] or 0)

    context = {
        'product': product,
        'main_categories':main_categories,
        'wcount':wcount,
        'reviews':reviews,
        'average_rating':average_rating,
        'wishCount': wish_count
    }
    
    return render(request, 'core/product-detail.html', context)


def add_product_review(request, product_id):
    if not request.user.is_authenticated:
        return redirect()

    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('products:product-detail-view', product_slug=product.slug )
    else:
        form = ProductReviewForm()
    return render(request, 'add_product_review.html', {'form': form, 'product': product})