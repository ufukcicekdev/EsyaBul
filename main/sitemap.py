from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from .models import *
from products.models import Product
from products.models import Category
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.sitemaps import Sitemap
from blog.models import Blog
startdate = datetime.today()
enddate = startdate + relativedelta(years=10)



class StaticViewSitemap(Sitemap):
    def items(self):
        return ['home','contact', 'about', 'faqs','blog']  

    def location(self, item):
        if item == 'home':
            return ''
        elif item == 'about':
            return '/about/'
        elif item == 'contact':
            return '/contact/'
        elif item == 'faqs':
            return '/faqs/'
        elif item == 'blog':
            return '/blog/'
        else:
            return reverse(item)



class ProductLinkSiteMap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Product.objects.filter(is_active=True)

    def location(self,obj):
        return f"/product/{obj.slug}"
    


class CategoryLinkSiteMap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self,obj):
        return f"/category/{obj.get_full_path_slug()}"
    


class BlogLinkSiteMap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Blog.objects.filter(is_active=True)

    def location(self, obj):
        return f"/blog/{obj.slug}"