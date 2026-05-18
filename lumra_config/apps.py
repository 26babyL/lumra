# lumra_config/apps.py
# Auto-updated oleh lumra_sync.py
# ready() diperlukan agar signals.py terdaftar saat Django startup

from django.apps import AppConfig


class LumraConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lumra_config'

    def ready(self):
        # Daftarkan signals — WAJIB agar auto stock deduction berjalan
        try:
            import lumra_config.signals  # noqa: F401
        except ImportError:
            pass
