import os
import environ # Pengganti decouple
from pathlib import Path
import logging.config
from celery.schedules import crontab
from datetime import timedelta

# 1. Inisialisasi environ
env = environ.Env(
    DEBUG=(bool, True), # Set default dan tipe data
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1'])
)

# 2. Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. Baca file .env (Pastikan file .env ada di root folder /lumra/)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ============ CORE SECURITY ============
# Tidak perlu pakai 'cast=bool' lagi karena sudah didefinisikan di atas
SECRET_KEY = env('SECRET_KEY', default='django-insecure-$@)ygpn3l2coujup$(0@_swfefep_0#re8-jzjb(u(!dz^pq^1')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ============ ENVIRONMENT ============
ENVIRONMENT = env('ENVIRONMENT', default='development')
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_DEVELOPMENT = ENVIRONMENT == 'development'

# ============ APPLICATION DEFINITION ============
INSTALLED_APPS = [
    # Admin UI (UNFOLD - Sudah disesuaikan)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.inlines',
    'unfold.contrib.import_export',
    
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.humanize',
    
    # Third-party UI & Frontend
    'theme',                  # Tailwind theme app lokal
    'crispy_forms',           # Terinstall 2.6
    'crispy_tailwind',        # Terinstall 1.0.3
    'django_extensions',
    'django_htmx',
    
    # Data Management
    'django_tables2',
    'django_filters',
    
    # REST API
    'rest_framework',         # Terinstall 3.17.1
    
    # Background Tasks
    'django_celery_beat',
    'django_celery_results',
    
    # Monitoring & Debugging
     'silk',            # Comment: Incompatible dengan Django 6.0
     'debug_toolbar',          # Comment: Testing tanpa app optional ini
    
    # Security
    'axes',
    
    # Utilities
    # 'weasyprint',             # Comment: Requires system libraries (GTK) yang tidak ada
    
    # Local Apps
    'lumra_config',
    'tailwind',
]

# ============ MIDDLEWARE STACK ============
MIDDLEWARE = [
    # Security
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    
    # Sessions & Auth
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # Third Party
    'django_htmx.middleware.HtmxMiddleware',
    'axes.middleware.AxesMiddleware',      # Brute force protection
    # 'silk.middleware.SilkyMiddleware',    # Comment: Incompatible dengan Django 6.0
    
    # Custom Middleware
    'lumra_config.middleware.EnsureUserProfileMiddleware',
    # 'lumra_system.middleware.logging_middleware.LumraRequestLoggingMiddleware', # Uncomment jika file ini ada
    
    # Development
    # *(['debug_toolbar.middleware.DebugToolbarMiddleware'] if IS_DEVELOPMENT else []),
    
    # XFrame protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lumra_system.urls'

# ============ TEMPLATES ============
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'lumra_config/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'lumra_config.context_processors.app_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'lumra_system.wsgi.application'
# ASGI_APPLICATION dihapus karena 'channels' TIDAK terinstall di list paket Anda

# ============ DATABASE CONFIGURATION ============
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='lumra_set_allegra'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='123456'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# ============ CACHING CONFIGURATION ============
# Disesuaikan karena 'django-redis' TIDAK terinstall, kita pakai Redis backend bawaan Django
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'KEY_PREFIX': 'lumra',
        'TIMEOUT': 300,
    }
}

# CacheOps (Karena package django-cacheops terinstall)
CACHEOPS_ENABLED = True
CACHEOPS_REDIS = env('REDIS_URL', default='redis://127.0.0.1:6379/1')
CACHEOPS_DEFAULTS = {
    'timeout': 60 * 60
}

# ============ CELERY CONFIGURATION ============
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Jakarta'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60
CELERY_ENABLE_UTC = False

CELERY_BEAT_SCHEDULE = {
    'refresh-materialized-views': {
        'task': 'lumra_config.tasks.refresh_materialized_views',
        'schedule': crontab(hour=2, minute=0),
    },
    'generate-daily-reports': {
        'task': 'lumra_config.tasks.generate_daily_reports',
        'schedule': crontab(hour=6, minute=0),
    },
    'cleanup-expired-sessions': {
        'task': 'lumra_config.tasks.cleanup_sessions',
        'schedule': crontab(hour=3, minute=0),
    },
}

# ============ JWT CONFIGURATION ============
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

# ============ REST FRAMEWORK ============
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # ← NEW: JWT First
        'rest_framework.authentication.SessionAuthentication',         # ← Fallback for Web UI
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# ============ CORS CONFIGURATION ============
# Hapus django-cors-headers karena TIDAK terinstall di list Anda
# CORS_ALLOWED_ORIGINS = config(...)

# ============ CRISPY FORMS ============
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# ============ TAILWIND CSS ============
TAILWIND_APP_NAME = 'theme'

# ============ DJANGO TABLES 2 ============
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap5.html'

# ============ SEARCH ENGINE (MeiliSearch) ============
MEILISEARCH_URL = env('MEILISEARCH_URL', default='http://127.0.0.1:7700')
MEILISEARCH_API_KEY = env('MEILISEARCH_API_KEY', default='masterKey')

# ============ SECURITY SETTINGS ============
if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    # CSP dihapus karena 'django-csp' tidak terinstall
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============ AXES (Brute Force Protection) ============
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_DURATION = 1
AXES_LOCKOUT_TEMPLATE = 'security/lockout.html'
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]

# ============ PASSWORD VALIDATION ============
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    # Ganti AxesModelBackend dengan ini (Solusi W003)
    'axes.backends.AxesStandaloneBackend',
    
    # Django ModelBackend bawaan
    'django.contrib.auth.backends.ModelBackend',
]

# ============ INTERNATIONALIZATION ============
LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# ============ STATIC FILES ============
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'lumra_config', 'static'),
]

# Hapus Whitenoise karena tidak terinstall
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============ MEDIA FILES ============
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============ AUTH SETTINGS ============
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# ============ APP VERSIONING ============
APP_VERSION = '2.0.0'
APP_NAME = 'Lumra - Advanced Inventory System'

# ============ DEBUG TOOLBAR ============
# INTERNAL_IPS = env.list('INTERNAL_IPS', default=['127.0.0.1', 'localhost'])

# if IS_DEVELOPMENT:
#     DEBUG_TOOLBAR_CONFIG = {
#         'SHOW_TOOLBAR_CALLBACK': lambda r: DEBUG,
#         'SHOW_TEMPLATE_CONTEXT': True,
#     }

# ============ LOGGING CONFIGURATION ============
# Formatter JSON dihapus karena 'python-json-logger' tidak terinstall
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/lumra.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'lumra_system': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if IS_DEVELOPMENT else 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}

os.makedirs('logs', exist_ok=True)

# ============ SENTRY CONFIGURATION ============
if IS_PRODUCTION:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    # RedisIntegration tidak di-import karena library integrasi redis spesifik sentry mungkin tidak ada
    
    sentry_sdk.init(
        dsn=env('SENTRY_DSN', default=''),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=ENVIRONMENT,
    )

# ============ DJANGO SILK PROFILING ============
SILKY_PYTHON_PROFILER_RESULT_LIMIT = 1000
SILKY_MAX_REQUEST_BODY_SIZE = -1  # Log all body
SILKY_MAX_RESPONSE_BODY_SIZE = -1
SILKY_META = False

# ============ CSRF & SECURITY ============
CSRF_TRUSTED_ORIGINS = env.list(
    'CSRF_TRUSTED_ORIGINS',
    default=['http://127.0.0.1:8000', 'http://localhost:8000']
)

# ============ UNFOLD ADMIN CUSTOMIZATION ============
UNFOLD = {
    "SITE_TITLE": "Lumra Admin",
    "SITE_HEADER": "Lumra Advanced System",
    "SITE_URL": "/",
    "SITE_ICON": lambda request: "/static/images/logo.svg",
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "production" if IS_PRODUCTION else "development",
    # "DASHBOARD_CALLBACK": "lumra_config.admin.dashboard_callback", # Uncomment jika file ini ada
}

# ============ PRODUCTION DEFAULTS ============
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============ EMAIL CONFIGURATION ============
EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@lumra.local')

print(f"✅ Django settings loaded successfully | Environment: {ENVIRONMENT} | Debug: {DEBUG}")

NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"