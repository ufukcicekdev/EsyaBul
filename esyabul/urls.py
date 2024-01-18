from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('customerauth.urls')),
    path('', include('main.urls')),
    path('', include('products.urls')),

     ##SOCIAL ACCOUNT
    path("social-auth/",include('social_django.urls',namespace='social')),

    path("ckeditor5/", include('django_ckeditor_5.urls')),

] + static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
