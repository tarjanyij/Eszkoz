from django.apps import AppConfig


class EszkozkezeloAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eszkozkezelo_app'
    
    def ready(self):
        import eszkozkezelo_app.signals