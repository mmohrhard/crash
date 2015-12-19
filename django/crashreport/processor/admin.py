from django.contrib import admin

from .models import ProcessedCrash, Signature

admin.site.register(ProcessedCrash)
admin.site.register(Signature)
