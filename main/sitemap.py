from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from .models import *
from products.models import Product
from products.models import Category
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.sitemaps import Sitemap

startdate = datetime.today()
enddate = startdate + relativedelta(years=10)





    
class ProductLinkSiteMap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Product.objects.filter(is_active=True)

    def location(self,obj):
        return f"/product/{obj.slug}"
    

