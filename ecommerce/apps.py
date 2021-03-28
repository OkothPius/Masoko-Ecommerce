from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    name = 'ecommerce'

    def ready(self):
        #import signal handlers
        import ecommerce.signals
