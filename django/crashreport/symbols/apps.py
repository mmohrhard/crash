from django.apps import AppConfig


class SymbolsConfig(AppConfig):
    name = 'symbols'

    def ready(self):
        import symbols.signals
