from django.urls import path, include
from blog.views import *

app_name = "blog"

urlpatterns = [
   path('blog', bloghome, name='blog_home'),
   path('blog/<slug:slug>/', blog_detail, name='blog_detail'),
   path('blogcategory/<slug:slug>/', category_detail, name='category_detail_blog'),
]
