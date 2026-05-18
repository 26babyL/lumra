import os
from pathlib import Path
from decouple import config, Csv
import logging.config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============ CORE SECURITY ============
SECRET_KEY = config('SECRET_KEY', default='django-insecure-$@)ygpn3l2coujup$(0@_swfefep_0#re8-jzjb(u(!dz^pq^1')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ============ ENVIRONMENT ============
ENVIRONMENT = config('ENVIRONMENT', default='development')
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_DEVELOPMENT = ENVIRONMENT == 'development'

# ============ APPLICATION DEFINITION ============
INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.humanize',
    
    # Admin UI
    'jazzmin',  # Harus sebelum django.contrib.admin
    
    # Third-party UI & Frontend
    'tailwind',
    'theme',
    'crispy_forms',
    'crispy_tailwind',
    'widget_tweaks',
    'django_extensions',
    'django_htmx',
    
    # Data Management
    'django_tables2',
    'django_filters',
    
    # Unfold Admin Interface
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.inlines',
    'unfold.contrib.import_export',
    
    # REST API
    'rest_framework',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'corsheaders',
    
    # Real-time & WebSockets
    'channels',
    
    # Background Tasks
    'django_celery_beat',
    'django_celery_results',
    
    # Monitoring & Logging
    'django_prometheus',
    
    # Security
    'axes',
    'csp',
    
    # Development Tools
    'debug_toolbar',
    'django_browser_reload',
    'django_silk',
    
    # Local Apps
    'lumra_config',
]

# ============ MIDDLEWARE STACK ============
MIDDLEWARE = [
    # Security & Monitoring
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files serving
    
    # Sessions & Auth
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS (sebelum CommonMiddleware)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # Request Processing
    'django_htmx.middleware.HtmxMiddleware',
    'axes.middleware.AxesMiddleware',  # Brute force protection
    'csp.middleware.CSPMiddleware',  # Content Security Policy
    
    # Custom Middleware
    'lumra_config.middleware.EnsureUserProfileMiddleware',
    'lumra_system.middleware.logging_middleware.LumraRequestLoggingMiddleware',
    
    # Monitoring (akhir)
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    
    # Development
    *(['debug_toolbar.middleware.DebugToolbarMiddleware'] if IS_DEVELOPMENT else []),
    *(['django_browser_reload.middleware.BrowserReloadMiddleware'] if IS_DEVELOPMENT else []),
    
    # XFrame protection (clickjacking)
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
            # Enable template caching in production
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ] if IS_PRODUCTION else None,
        },
    },
]

WSGI_APPLICATION = 'lumra_system.wsgi.application'
ASGI_APPLICATION = 'lumra_system.asgi.application'  # Untuk Channels/WebSockets

# ============ DATABASE CONFIGURATION ============
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='lumra_set_allegra'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='123456'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        # Connection pooling
        'CONN_MAX_AGE': 600,  # Reuse connections for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=read_committed'
        },
    }
}

# Database Router untuk Read-Write Splitting (jika sudah ada read replicas)
# DATABASE_ROUTERS = ['lumra_system.routers.PrimaryReplicaRouter']

# ============ CACHING CONFIGURATION ============
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_KWARGS': {'encoding': 'utf8'},
            'POOL_KWARGS': {'max_connections': 50, 'retry_on_timeout': True},
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Fallback jika Redis down
        },
        'KEY_PREFIX': 'lumra',
        'TIMEOUT': 300,  # 5 menit default timeout
    }
}

# Cachalot (auto query caching)
CACHALOT_ENABLED = True
CACHALOT_TIMEOUT = 3600  # 1 jam untuk cache results

# ============ CELERY CONFIGURATION ============
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Jakarta'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit
CELERY_ENABLE_UTC = False

# Beat schedule untuk periodic tasks
CELERY_BEAT_SCHEDULE = {
    'refresh-materialized-views': {
        'task': 'lumra_config.tasks.refresh_materialized_views',
        'schedule': crontab(hour=2, minute=0),  # Jam 2 pagi setiap hari
    },
    'generate-daily-reports': {
        'task': 'lumra_config.tasks.generate_daily_reports',
        'schedule': crontab(hour=6, minute=0),  # Jam 6 pagi
    },
    'cleanup-expired-sessions': {
        'task': 'lumra_config.tasks.cleanup_sessions',
        'schedule': crontab(hour=3, minute=0),  # Jam 3 pagi
    },
}

# ============ CHANNELS CONFIGURATION ============
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [config('REDIS_URL', default='redis://127.0.0.1:6379/3')],
        },
    },
}

# ============ REST FRAMEWORK ============
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# DRF Spectacular (OpenAPI Schema)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Lumra API',
    'DESCRIPTION': 'Sistem Manajemen Inventory & Bisnis Terpadu',
    'VERSION': '1.0.0',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    'SERVE_AUTHENTICATION': ['rest_framework.authentication.SessionAuthentication'],
    'SCHEMA_PATH_PREFIX': '/api/v[0-9]',
    'PREPROCESSING_HOOKS': ['lumra_config.api.preprocessing.preprocess_schema_request'],
}

# ============ CORS CONFIGURATION ============
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True

# ============ CRISPY FORMS ============
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# ============ TAILWIND ============
TAILWIND_APP_NAME = 'theme'

# ============ DJANGO TABLES 2 ============
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap5.html'

# ============ SEARCH ENGINE (MeiliSearch) ============
MEILISEARCH_URL = config('MEILISEARCH_URL', default='http://127.0.0.1:7700')
MEILISEARCH_API_KEY = config('MEILISEARCH_API_KEY', default='masterKey')

# ============ SECURITY SETTINGS ============
if IS_PRODUCTION:
    # SSL/TLS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": ("'self'",),
        "script-src": ("'self'", "'unsafe-inline'", "cdn.tailwindcss.com"),
        "style-src": ("'self'", "'unsafe-inline'", "cdn.tailwindcss.com"),
        "img-src": ("'self'", "data:", "https:"),
    }
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============ AXES (Brute Force Protection) ============
AXES_FAILURE_LIMIT = 5  # 5 percobaan gagal
AXES_COOLOFF_DURATION = 1  # 1 jam lockout
AXES_LOCKOUT_TEMPLATE = 'security/lockout.html'
AXES_USE_USER_AGENT = True
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True

# ============ PASSWORD VALIDATION ============
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Lebih ketat
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============ INTERNATIONALIZATION ============
LANGUAGE_CODE = 'id'  # Indonesian
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# ============ STATIC FILES ============
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'lumra_config', 'static'),
]

# WhiteNoise untuk serving static files efficiently di production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' if IS_PRODUCTION else 'django.contrib.staticfiles.storage.StaticFilesStorage'

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
INTERNAL_IPS = config('INTERNAL_IPS', default='127.0.0.1,localhost', cast=Csv())

if IS_DEVELOPMENT:
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda r: DEBUG,
        'SHOW_TEMPLATE_CONTEXT': True,
        'ENABLE_STACKTRACES': True,
        'SQL_WARNING_THRESHOLD': 500,  # ms
        'PROFILER_MAX_DEPTH': 10,
    }

# ============ LOGGING CONFIGURATION ============
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
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
        'file_json': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/lumra_json.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
            'formatter': 'json',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'lumra_system': {
            'handlers': ['console', 'file', 'file_json'],
            'level': 'DEBUG' if IS_DEVELOPMENT else 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}

# Buat logs directory jika belum ada
os.makedirs('logs', exist_ok=True)

# ============ SENTRY CONFIGURATION ============
if IS_PRODUCTION:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=config('SENTRY_DSN', default=''),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=ENVIRONMENT,
    )

# ============ PROMETHEUS METRICS ============
PROMETHEUS_EXPORT_MIGRATIONS = True

# ============ CSRF & SECURITY ============
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://127.0.0.1:8000,http://localhost:8000',
    cast=Csv()
)

# ============ JAZZMIN ADMIN CUSTOMIZATION ============
JAZZMIN_SETTINGS = {
    "site_title": "Lumra Admin",
    "site_header": "Lumra Management System",
    "site_brand": "Lumra",
    "welcome_sign": "Selamat datang di Admin Lumra",
    "search_model": ["auth.User", "auth.Group"],
    "user_avatar": None,
    "show_ui_builder": IS_DEVELOPMENT,
    "navigation_expanded": True,
    "hideout_apps": [],
    "default_icon_parents": "fas fa-chevron-right",
    "default_icon_children": "fas fa-arrow-right",
}

# ============ UNFOLD ADMIN CUSTOMIZATION ============
UNFOLD = {
    "SITE_TITLE": "Lumra Admin",
    "SITE_HEADER": "Lumra Advanced System",
    "SITE_URL": "/",
    "SITE_ICON": lambda request: "/static/images/logo.svg",
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "production" if IS_PRODUCTION else "development",
    "DASHBOARD_CALLBACK": "lumra_config.admin.dashboard_callback",
}

# ============ PRODUCTION DEFAULTS ============
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============ NOM_BIN_PATH untuk Windows ============
NPM_BIN_PATH = config('NPM_BIN_PATH', default=r"C:\Program Files\nodejs\npm.cmd")

# ============ EMAIL CONFIGURATION ============
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@lumra.local')

# ============ DJANGO SILK PROFILING ============
SILK_PROFILING_ENABLED = IS_DEVELOPMENT
SILK_HIDE_PRIVATES = True
SILK_HIDE_REQUESTS_NEWER_THAN_HOURS = 24

print(f"✅ Django settings loaded successfully | Environment: {ENVIRONMENT} | Debug: {DEBUG}")
