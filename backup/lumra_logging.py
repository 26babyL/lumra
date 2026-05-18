# =============================================================
# LUMRA LOGGING SYSTEM — Enterprise Grade
# Letakkan konfigurasi ini di lumra_system/settings.py
# =============================================================
#
# STRUKTUR LOG YANG DIHASILKAN:
#   logs/
#   ├── debug.log         → semua aktivitas (dev only)
#   ├── error.log         → error & critical saja
#   ├── security.log      → login gagal, akses ditolak
#   └── performance.log   → query lambat, response time
#
# =============================================================

import os
from pathlib import Path

# Pastikan folder logs/ ada
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    # ----------------------------------------------------------
    # FORMATTERS — Format pesan log
    # ----------------------------------------------------------
    'formatters': {

        # Format lengkap untuk file log
        'verbose': {
            'format': (
                '[{asctime}] {levelname:<8} | '
                'PID:{process} | '
                '{name} | '
                '{module}.{funcName}():{lineno} | '
                '{message}'
            ),
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },

        # Format ringkas untuk console (development)
        'simple': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        },

        # Format khusus security
        'security': {
            'format': (
                '[{asctime}] SECURITY | '
                '{levelname} | '
                'IP:{request_ip} | '
                'User:{username} | '
                '{message}'
            ),
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },

    # ----------------------------------------------------------
    # FILTERS — Filter log berdasarkan kondisi
    # ----------------------------------------------------------
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },

    # ----------------------------------------------------------
    # HANDLERS — Kemana log dikirim
    # ----------------------------------------------------------
    'handlers': {

        # Console — hanya aktif saat DEBUG=True
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },

        # error.log — semua ERROR & CRITICAL (termasuk production)
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'error.log',
            'maxBytes': 10 * 1024 * 1024,   # 10 MB per file
            'backupCount': 10,               # simpan 10 file lama
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },

        # debug.log — semua level (dev only)
        'file_debug': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'debug.log',
            'maxBytes': 20 * 1024 * 1024,   # 20 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },

        # security.log — login, permission, auth events
        'file_security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 5 * 1024 * 1024,    # 5 MB
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },

        # performance.log — query lambat & slow responses
        'file_performance': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'performance.log',
            'maxBytes': 10 * 1024 * 1024,   # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },

        # Email admin kalau ada CRITICAL error di production
        'mail_admins': {
            'level': 'CRITICAL',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },

    # ----------------------------------------------------------
    # LOGGERS — Siapa yang mencatat apa
    # ----------------------------------------------------------
    'loggers': {

        # Django core
        'django': {
            'handlers': ['console', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },

        # Request HTTP — catat 404, 500, dll
        'django.request': {
            'handlers': ['file_error', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },

        # Template errors — TemplateSyntaxError, TemplateNotFound, dll
        'django.template': {
            'handlers': ['console', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },

        # Database queries
        'django.db.backends': {
            'handlers': ['file_performance'],
            'level': 'WARNING',  # Ganti ke DEBUG untuk lihat semua query
            'propagate': False,
        },

        # Security & Auth
        'django.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },

        # Logger khusus Lumra — pakai ini di seluruh views/models
        'lumra': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },

        # Logger khusus untuk performa (query lambat, dll)
        'lumra.performance': {
            'handlers': ['file_performance'],
            'level': 'WARNING',
            'propagate': False,
        },

        # Logger untuk proses seeding & management commands
        'lumra.seed': {
            'handlers': ['console', 'file_debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# =============================================================
# CARA PAKAI DI VIEWS / MODELS / ANYWHERE
# =============================================================
#
# import logging
# logger = logging.getLogger('lumra')
#
# logger.debug("Detail info untuk debugging")
# logger.info("Proses normal berjalan")
# logger.warning("Ada yang perlu diperhatikan")
# logger.error("Ada error tapi sistem masih jalan")
# logger.critical("Sistem mungkin down!")
#
# --- Contoh di views.py ---
#
# import logging
# logger = logging.getLogger('lumra')
#
# def product_list(request):
#     try:
#         products = Product.objects.select_related('category').all()
#         logger.info(f"product_list accessed by user={request.user}")
#         return render(request, 'products/list.html', {'products': products})
#     except Exception as e:
#         logger.error(f"Gagal load product_list: {e}", exc_info=True)
#         # exc_info=True → otomatis catat full traceback ke log!
#         raise
#
# =============================================================