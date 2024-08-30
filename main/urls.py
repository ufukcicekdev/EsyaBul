from django.urls import path,include
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
from .views import *
from django.contrib.sitemaps.views import sitemap
from main.sitemap import ProductLinkSiteMap,StaticViewSitemap,CategoryLinkSiteMap,BlogLinkSiteMap

app_name = "main"


sitemaps = {
    'static': StaticViewSitemap,
    'CategoryLinkSiteMap':CategoryLinkSiteMap, 
    'ProductLinkSiteMap':ProductLinkSiteMap, 
    "BlogLinkSiteMap":BlogLinkSiteMap,
}


urlpatterns = [
    path('', home, name='home'),
    path('my_style/', my_style_start, name='my_style_start'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('faqs/', faqs, name='faqs'),
    path('how-does-it-work/', does_it_work, name='itwork'),
    path("contact-form/", ajax_contact_form, name="ajax-contact-form"),
    path("category/<path:category_slugs>/", dynamic_category_product_list_view, name="dynamic-category-product-list"),
    path('search/', search_view, name='search_results'),
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt',TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]



