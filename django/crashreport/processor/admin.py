from django.contrib import admin

from .models import ProcessedCrash, Signature, CrashCount

admin.site.register(ProcessedCrash)
admin.site.register(Signature)
admin.site.register(CrashCount)
