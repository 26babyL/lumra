# ============================================================================
# LUMRA SETTINGS.PY - PRODUCTION-READY ADDITIONS
# Add these sections to your existing lumra_system/settings.py
# 
# Implementation Priority: JWT → Accounting → DB Scalability → Permissions
# Total Lines: ~250 lines to add (insert into appropriate sections)
# ============================================================================

# ============ 1. JWT AUTHENTICATION (Add after REST_FRAMEWORK) ============

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
    'SLIDING_TOKEN_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# ============ 2. UPGRADE REST_FRAMEWORK ============

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # ← NEW: JWT first
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
    'DEFAULT_THROTTLE_CLASSES': [  # ← NEW: Rate limiting
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# ============ 3. ACCOUNTING CONFIGURATION (Add new section) ============

from decimal import ROUND_HALF_UP

ACCOUNTING_PRECISION = {
    'MAX_DIGITS': 18,                          # ISO 20022 compliance
    'DECIMAL_PLACES': 2,                       # Currency precision
    'ROUNDING_MODE': ROUND_HALF_UP,           # Standard rounding
}

ACCOUNTING_MODULE = {
    'ENABLED': True,
    'DEFAULT_BRANCH_CURRENCY': 'IDR',
    'FISCAL_YEAR_START_MONTH': 1,              # January start
    'CONSOLIDATION_RULES': 'branch_level',     # or 'company_level'
    'INTER_BRANCH_TRANSACTIONS': True,
    'AUTO_JOURNAL_TRANSACTIONS': True,
    'JOURNAL_APPROVAL_REQUIRED': False,
    'AUDIT_ALL_GL_ENTRIES': True,
    'REQUIRE_GL_REFERENCE': True,
    
    # Chart of Accounts prefixes (modify for your COA structure)
    'COA_PREFIX': {
        'ASSET': '1',
        'LIABILITY': '2',
        'EQUITY': '3',
        'REVENUE': '4',
        'COGS': '5',
        'EXPENSE': '6',
    },
}

# ============ 4. DATABASE SCALABILITY (Replace DATABASES section) ============

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='lumra_set_allegra'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='123456'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        
        # ✅ Connection Pooling for 1M+ records
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': False,
        
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=read_committed',
            'keepalives': 1,
            'keepalives_idle': 30,
            'sslmode': 'prefer' if IS_PRODUCTION else 'disable',
        },
    },
    
    # ✅ Optional: Read Replica for analytics/reports (separate server)
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_REPLICA_NAME', default='lumra_set_allegra'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='123456'),
        'HOST': env('DB_REPLICA_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        },
    } if env.bool('DB_REPLICA_ENABLED', default=False) else {},
}

# ============ 5. DATABASE ROUTING (Multi-database read/write split) ============

DATABASE_ROUTERS = ['lumra_config.routers.PrimaryReplicaRouter'] if env.bool('DB_REPLICA_ENABLED', default=False) else []

# ============ 6. CACHING CONFIGURATION (Enhanced) ============

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django.core.cache.backends.redis.RedisCache',
            'IGNORE_EXCEPTIONS': True,  # Fail gracefully if Redis down
        },
        'KEY_PREFIX': 'lumra',
        'TIMEOUT': 300,  # 5 minutes default
    },
    # ✅ Separate cache for sessions
    'session': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_SESSION_URL', default='redis://127.0.0.1:6379/3'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django.core.cache.backends.redis.RedisCache',
        },
        'KEY_PREFIX': 'session',
    },
}

# ✅ Session storage (very fast)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'session'

# ✅ Cache timeout strategy for different data types
CACHE_TIMEOUT_STRATEGY = {
    'product': 3600,           # 1 hour (products change slowly)
    'stock': 300,              # 5 minutes (stock changes frequently)
    'exchange_rate': 86400,    # 24 hours (stable)
    'branch_config': 3600,     # 1 hour
    'user_permissions': 1800,  # 30 minutes
}

# ============ 7. CELERY OPTIMIZATION ============

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

# ✅ NEW: Task routing for priority queues
CELERY_TASK_ROUTING = {
    'lumra_config.tasks.critical_*': {'queue': 'critical', 'routing_key': 'task.critical'},
    'lumra_config.tasks.background_*': {'queue': 'background', 'routing_key': 'task.background'},
}

# ✅ NEW: Performance tuning
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

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
    
    # ✅ NEW: Health check
    'celery-health-check': {
        'task': 'lumra_config.tasks.celery_health_check',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    
    # ✅ NEW: Cache warmup
    'warm-product-cache': {
        'task': 'lumra_config.tasks.warm_product_cache',
        'schedule': crontab(hour='*/4'),  # Every 4 hours
    },
    
    # ✅ NEW: Accounting reconciliation
    'daily-gl-reconciliation': {
        'task': 'lumra_config.tasks.daily_gl_reconciliation',
        'schedule': crontab(hour=23, minute=30),  # 11:30 PM
    },
}

# ============ 8. SECURITY ENHANCEMENTS ============

# ✅ NEW: Permission and decorator setup
LUMRA_SECURITY = {
    'ENABLE_BRANCH_ISOLATION': True,
    'REQUIRE_ACCOUNTING_APPROVAL': False,
    'AUDIT_LOG_ALL_CHANGES': True,
    'SESSION_TIMEOUT': 3600,  # 1 hour
}

# ✅ NEW: Accounting-specific authentication
ACCOUNTING_DECORATORS_ENABLED = True

# ============ 9. MULTI-BRANCH SUPPORT ============

MULTI_BRANCH_CONFIG = {
    'ENABLED': True,
    'BRANCH_ISOLATION_LEVEL': 'row_level_security',  # PostgreSQL RLS
    'MAX_BRANCHES': 32,
    'DEFAULT_BRANCH_ID': env.int('DEFAULT_BRANCH_ID', default=1),
}

# ============ 10. MIDDLEWARE UPDATES (Add to existing MIDDLEWARE list) ============

# Add these to your MIDDLEWARE list (order matters):
# MIDDLEWARE = [
#     ...existing middleware...
#     'lumra_config.middleware.BranchIsolationMiddleware',  # ← ADD THIS
# ]

# ============ 11. INSTALLED APPS (Verify/Add) ============

# Ensure these are in INSTALLED_APPS:
# 'rest_framework',                    # ← Should be there
# 'rest_framework_simplejwt',          # ← NEW: Add this
# 'django_filters',                    # ← Should be there
# 'lumra_config',                      # ← Should be there

# ============ 12. QUERY OPTIMIZATION HINTS ============

DB_PERFORMANCE_HINTS = {
    'enable_select_related': True,
    'enable_prefetch_related': True,
    'batch_size': 500,  # For bulk operations
    'use_in_bulk_create': True,
}

# ============ 13. LOGGING ENHANCEMENTS ============

# Add to LOGGING['loggers']:
LOGGING['loggers'].update({
    'accounting': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
        'propagate': False,
    },
    'audit': {
        'handlers': ['file'],
        'level': 'DEBUG',
        'propagate': False,
    },
})

# ============ 14. ENVIRONMENT VARIABLES TO ADD TO .ENV ============

# Add these to your .env file:
"""
# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Database Replica (optional)
DB_REPLICA_ENABLED=False
DB_REPLICA_HOST=localhost
DB_REPLICA_NAME=lumra_set_allegra

# Redis (already there, verify)
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/2
REDIS_SESSION_URL=redis://127.0.0.1:6379/3

# Branch Configuration
DEFAULT_BRANCH_ID=1

# Accounting
ACCOUNTING_ENABLED=True
REQUIRE_ACCOUNTING_APPROVAL=False
"""

# ============================================================================
# IMPLEMENTATION STEPS:
# ============================================================================
#
# 1. Add 'rest_framework_simplejwt' to requirements.in:
#    djangorestframework-simplejwt==5.3.2
#
# 2. Run: pip-compile && pip install -r requirements.txt
#
# 3. Paste sections 1-14 into settings.py in appropriate places
#
# 4. Create files:
#    - lumra_config/routers.py (database router)
#    - lumra_config/middleware.py (branch isolation)
#    - lumra_config/decorators.py (permission decorators)
#    - lumra_config/validators.py (accounting validators)
#
# 5. Create migration for accounting precision:
#    python manage.py makemigrations --name fix_accounting_precision
#
# 6. Test JWT endpoints:
#    POST /api/auth/token/
#    {"username": "user", "password": "pass"}
#
# 7. Run load testing before production deployment
#
# ============================================================================
