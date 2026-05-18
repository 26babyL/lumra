from django.conf import settings

def app_settings(request):
    """
    Context processor untuk membuat pengaturan aplikasi tersedia di semua template.
    Ini memungkinkan kita untuk mengelola versi dan info lainnya dari settings.py.
    """
    return {
        # Ambil APP_VERSION dari settings.py, dengan nilai default jika tidak ada
        'app_version': getattr(settings, 'APP_VERSION', '1.0.0'),
    }