from django.contrib import admin

from .models import Product
from .models import Version

admin.site.register(Product)
admin.site.register(Version)
