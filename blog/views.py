from django.shortcuts import render,get_object_or_404
from blog.models import *
from django.contrib import messages
from main.mainContent import mainContent
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger






def bloghome(request):
    try:
        mainContext = mainContent(request)

        description = (
            "Esyala Blog: Dekorasyon, yaşam tarzı ve teknoloji ile ilgili en son haberler ve rehber yazılarla ilham alın. Ev ve yaşamınızı yenileyin."
        )
        mainContext["description"] = description
        
        blogs_list = Blog.objects.filter(is_active=True).order_by('-created_at')
        popular_posts = Blog.objects.filter(is_active=True, views__gt=10).order_by('-created_at')


        categories = Category.objects.filter(is_active=True)

        paginator = Paginator(blogs_list, 10)  
        page = request.GET.get('page')

        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

    except Exception as e:
        messages.error(request, "Bloglar yüklenirken bir hata oluştu.")
        blogs = []
        categories = []

    context = {
        "blogs": blogs,
        "categories": categories,
        "popular_posts":popular_posts
    }

    context.update(mainContext)
    return render(request, 'blog/bloghome.html', context)






def blog_detail(request, slug):
    try:
        mainContext = mainContent(request)
        blog = get_object_or_404(Blog, slug=slug, is_active=True)
        mainContext["description"] = blog.short_description
        categories = Category.objects.filter(is_active=True)
        popular_posts = Blog.objects.filter(is_active=True, views__gt=10).order_by('-created_at')
        blog.views += 1
        blog.save()
        
        context = {
            'blog': blog,
            "categories":categories,
            "popular_posts":popular_posts
        }
        context.update(mainContext)
        return render(request, 'blog/blogdetail.html', context)
    
    except Exception as e:
        messages.error(request, "Blog detayları yüklenirken bir hata oluştu.")
        return render(request, 'blog/blog_detail.html', {'blog': None})
    


def category_detail(request, slug):
    try:
        mainContext = mainContent(request)

        category = get_object_or_404(Category, slug=slug, is_active=True)
        categories = Category.objects.filter(is_active=True)
        mainContext["description"] = category.description

        category_blogs = Blog.objects.filter(category=category, is_active=True).order_by('-created_at')
        popular_posts = Blog.objects.filter(is_active=True, views__gt=10).order_by('-created_at')

    except Exception as e:
        messages.error(request, "Kategori yüklenirken bir hata oluştu.")
        category_blogs = []

    context = {
        "category": category,
        "categories":categories,
        "category_blogs": category_blogs,
        "popular_posts":popular_posts
    }
    context.update(mainContext)
    return render(request, 'blog/category_detail.html', context)