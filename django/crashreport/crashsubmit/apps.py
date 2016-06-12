from django.apps import AppConfig


class CrashsubmitConfig(AppConfig):
    name = 'crashsubmit'

    def ready(self):
        import crashsubmit.signals
