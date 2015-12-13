from django.contrib import admin

# Register your models here.

from .models import UploadedCrash
from .models import Product
from .models import Version

admin.site.register(UploadedCrash)
admin.site.register(Product)
admin.site.register(Version)
