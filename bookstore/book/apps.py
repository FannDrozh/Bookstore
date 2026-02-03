from django.apps import AppConfig


class BookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'book'
    verbose_name = 'Управление книгами'

    def ready(self):
        """Импорт сигналов при запуске приложения"""
        try:
            import book.signals
        except ImportError:
            pass