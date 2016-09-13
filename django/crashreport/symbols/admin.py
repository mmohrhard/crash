from django.contrib import admin

from .models import SymbolsUpload, MissingSymbolConfig, MissingSymbol

admin.site.register(SymbolsUpload)
admin.site.register(MissingSymbolConfig)
admin.site.register(MissingSymbol)
