from django.contrib import admin
from django.urls import path, include
from esyabul.settings import base
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('customerauth.urls')),
    path('', include('main.urls')),
    path('', include('products.urls')),
    path('', include('notification.urls')),
    path('', include('payment.urls')),
    path("social-auth/", include('social_django.urls', namespace='social')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

if base.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(base.STATIC_URL, document_root=base.STATIC_ROOT)
    urlpatterns += static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)



handler404 = "main.views.custom_404_page"
handler500 = "main.views.custom_500_page"
