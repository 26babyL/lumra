# 🚀 LUMRA DJANGO UPGRADE GUIDE - BEAST MODE

## 📋 Daftar Isi
1. [Overview Arsitektur](#overview-arsitektur)
2. [Installation Guide](#installation-guide)
3. [Konfigurasi Environment](#konfigurasi-environment)
4. [Setup Individual Components](#setup-individual-components)
5. [Best Practices & Optimization](#best-practices--optimization)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## 🏗️ Overview Arsitektur

Stack Lumra Anda sekarang akan terlihat seperti ini:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                             │
│  (Browser: HTMX + Alpine.js + Tailwind CSS)               │
└────────────────┬──────────────────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
┌─────▼────┐         ┌─────▼─────┐
│  HTTP    │         │ WebSocket │
│  SYNC    │         │ ASYNC     │
└─────┬────┘         └─────┬─────┘
      │                    │
      └──────────┬─────────┘
                 │
        ┌────────▼────────┐
        │  DJANGO ASGI    │
        │  (Daphne)       │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│ VIEWS  │  │ TASKS  │  │ WSGI   │
│ LOGIC  │  │(Celery)│  │ HTTP   │
└───┬────┘  └───┬────┘  └───┬────┘
    │           │           │
    └───────────┼───────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼────┐  ┌──▼───┐  ┌────▼────┐
│DATABASE│  │CACHE │  │ SEARCH  │
│(PG)    │  │(Redis)│  │Engine   │
└────────┘  └───────┘  └─────────┘
```

### Komponen Utama:

| Komponen | Purpose | Tech Stack |
|----------|---------|-----------|
| **Frontend** | UI/UX modern | HTMX, Alpine.js, Tailwind, Unfold |
| **Application** | Business logic | Django 6.0 + DRF |
| **Real-time** | WebSocket updates | Django Channels |
| **Background** | Heavy processing | Celery + Redis |
| **Caching** | Query optimization | Redis + Cachalot |
| **Search** | Full-text search | MeiliSearch |
| **Database** | Data persistence | PostgreSQL 13+ |
| **Monitoring** | Error tracking | Sentry + Prometheus |
| **API Docs** | Developer docs | drf-spectacular |

---

## 🔧 Installation Guide

### Step 1: Backup Existing Project
```bash
# Backup settings & requirements
cp lumra_system/settings.py lumra_system/settings.backup.py
cp requirements.txt requirements.backup.txt
```

### Step 2: Install New Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install dari file requirements
pip install -r requirements.txt

# Untuk development dengan pre-commit hooks
pip install pre-commit
pre-commit install
```

### Step 3: Update Django Settings
```bash
# Backup lama
mv lumra_system/settings.py lumra_system/settings_old.py

# Copy settings baru (yang sudah disediakan)
cp settings_production.py lumra_system/settings.py
```

### Step 4: Create .env File
Buat file `.env` di root project:

```bash
# Django Core
SECRET_KEY=your-super-secret-key-here-change-in-production
DEBUG=False
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=lumra_set_allegra
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis (Cache, Celery, Channels)
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/2

# Search Engine (MeiliSearch)
MEILISEARCH_URL=http://127.0.0.1:7700
MEILISEARCH_API_KEY=masterKey

# Sentry (Error Tracking) - Optional
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@lumra.local

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Internal IPs (untuk Debug Toolbar)
INTERNAL_IPS=127.0.0.1,localhost

# Node.js path (Windows)
NPM_BIN_PATH=C:\Program Files\nodejs\npm.cmd
```

### Step 5: Create Required Directories
```bash
mkdir -p logs
mkdir -p lumra_config/static
mkdir -p lumra_config/templates
mkdir -p media
```

### Step 6: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --run-syncdb
```

---

## 📦 Konfigurasi Environment

### Development Setup

**PostgreSQL Installation** (jika belum ada):
```bash
# Windows (gunakan installer dari postgresql.org)
# atau via Chocolatey:
choco install postgresql

# Linux (Ubuntu/Debian):
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql
```

**Redis Installation**:
```bash
# Windows: Download dari https://github.com/microsoftarchive/redis/releases
# atau via Chocolatey:
choco install redis

# Linux:
sudo apt-get install redis-server

# macOS:
brew install redis

# Start Redis
redis-server

# Test
redis-cli ping  # Should return "PONG"
```

**MeiliSearch Installation** (Optional tapi recommended):
```bash
# Windows:
# Download dari https://github.com/meilisearch/meilisearch/releases

# Linux:
sudo apt-get install meilisearch-http

# macOS:
brew install meilisearch

# Start
meilisearch --env development
```

### Production Setup (dengan Docker)

Buat `docker-compose.yml`:

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: lumra_set_allegra
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  meilisearch:
    image: getmeili/meilisearch:latest
    environment:
      MEILI_MASTER_KEY: masterKey
    ports:
      - "7700:7700"
    volumes:
      - meilisearch_data:/meili_data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7700/health"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
  meilisearch_data:
```

Run:
```bash
docker-compose up -d
```

---

## 🔌 Setup Individual Components

### 1. CACHING LAYER

**File: `lumra_config/cache.py`**
```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django_cachalot.decorators import cachalot_invalidate

def get_categories_cached():
    """Get all categories from cache, atau dari DB jika cache empty"""
    key = 'categories:all'
    categories = cache.get(key)
    if categories is None:
        categories = Category.objects.all()
        cache.set(key, categories, timeout=3600)  # 1 hour
    return categories

def invalidate_cache(sender, instance, **kwargs):
    """Invalidate cache ketika data berubah"""
    cache.delete('categories:all')
    cache.delete('products:summary')

# Gunakan di models.py
from django.db.models.signals import post_save, post_delete
post_save.connect(invalidate_cache, sender=Category)
```

### 2. BACKGROUND TASKS (Celery)

**File: `lumra_config/celery.py`**
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_system.settings')

app = Celery('lumra_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**File: `lumra_config/tasks.py`**
```python
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def generate_daily_reports(self):
    """Generate laporan harian - jalankan setiap jam 6 pagi"""
    try:
        # Heavy calculation logic
        logger.info("Generating daily reports...")
        # ... your code ...
    except Exception as exc:
        # Retry dengan exponential backoff
        raise self.retry(exc=exc, countdown=60)

@shared_task
def refresh_materialized_views():
    """Refresh materialized views - jalankan setiap jam 2 pagi"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY vw_sales_summary")
    logger.info("Materialized views refreshed")

@shared_task
def send_low_stock_alerts():
    """Notifikasi stok menipis kepada manager"""
    from lumra_inventory.models import Product
    low_stock = Product.objects.filter(stock__lt=10)
    # Send notifications...
    logger.info(f"Sent alerts for {low_stock.count()} products")
```

**Run Celery Worker:**
```bash
# Terminal 1: Celery Worker (memproses tasks)
celery -A lumra_system worker -l info

# Terminal 2: Celery Beat (scheduler untuk periodic tasks)
celery -A lumra_system beat -l info

# Production: Gunakan supervisord atau systemd
```

### 3. REAL-TIME UPDATES (Django Channels)

**File: `lumra_config/consumers.py`**
```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class StockUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """User connect ke WebSocket"""
        self.room_name = 'stock_updates'
        self.room_group_name = f'stock_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """User disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def stock_message(self, event):
        """Receive message dari group & kirim ke WebSocket"""
        message = event['message']
        await self.send(text_data=json.dumps(message))
```

**File: `lumra_config/routing.py`**
```python
from django.urls import re_path
from lumra_config.consumers import StockUpdateConsumer

websocket_urlpatterns = [
    re_path(r'ws/stock/$', StockUpdateConsumer.as_asgi()),
]
```

**Update `lumra_system/asgi.py`:**
```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import lumra_config.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_system.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            lumra_config.routing.websocket_urlpatterns
        )
    ),
})
```

**HTML Template:**
```html
<script>
    const stockSocket = new WebSocket(`ws://${window.location.host}/ws/stock/`);
    
    stockSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        // Update DOM dengan data terbaru
        document.getElementById('stock-' + data.product_id).innerHTML = data.stock;
    };
</script>
```

### 4. FULL-TEXT SEARCH (MeiliSearch)

**File: `lumra_config/search.py`**
```python
import meilisearch
from django.conf import settings

client = meilisearch.Client(
    settings.MEILISEARCH_URL,
    settings.MEILISEARCH_API_KEY
)

def index_products():
    """Index semua produk ke MeiliSearch"""
    from lumra_inventory.models import Product
    
    products = Product.objects.values(
        'id', 'name', 'description', 'price', 'category__name'
    )
    
    index = client.index('products')
    index.add_documents(list(products))

def search_products(query):
    """Cari produk dengan Google-like experience"""
    index = client.index('products')
    results = index.search(
        query,
        {
            'attributesToSearchOn': ['name', 'description'],
            'attributesToHighlight': ['name', 'description'],
            'limit': 20,
        }
    )
    return results['hits']
```

### 5. DATABASE OPTIMIZATION

**File: `lumra_config/models.py` (Database indexes)**
```python
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)  # BTree index
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    stock = models.IntegerField(db_index=True)  # Untuk filter stok
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # GIN index untuk full-text search
    search_vector = SearchVectorField(null=True, blank=True)
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['category', 'stock']),  # Composite index
            models.Index(fields=['created_at', '-price']),
        ]
```

**SQL Optimization - Materialized View:**
```sql
-- Buat materialized view untuk laporan summary
CREATE MATERIALIZED VIEW vw_sales_summary AS
SELECT
    p.category_id,
    DATE_TRUNC('month', t.created_at)::date as month,
    COUNT(*) as total_transactions,
    SUM(t.total_amount) as total_sales,
    AVG(t.total_amount) as avg_transaction
FROM transactions t
JOIN products p ON t.product_id = p.id
GROUP BY p.category_id, DATE_TRUNC('month', t.created_at);

-- Create index pada materialized view
CREATE INDEX idx_sales_summary_category_month 
ON vw_sales_summary(category_id, month);

-- Refresh command (jalankan via Celery)
REFRESH MATERIALIZED VIEW CONCURRENTLY vw_sales_summary;
```

### 6. MONITORING & LOGGING

**File: `lumra_config/logging_config.py`**
```python
import logging
from pythonjsonlogger import jsonlogger

# JSON logger untuk production
handler = logging.FileHandler('logs/lumra_json.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)

logger = logging.getLogger('lumra_system')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage:
logger.info('Product purchased', extra={
    'user_id': 123,
    'product_id': 456,
    'quantity': 5,
    'amount': 150000
})
```

### 7. API DOCUMENTATION

Setelah setup, dokumentasi auto-generate tersedia di:
```
http://localhost:8000/api/schema/swagger-ui/
http://localhost:8000/api/schema/redoc/
```

---

## ⚡ Best Practices & Optimization

### Query Optimization Checklist:

```python
# ❌ BAD - N+1 Query Problem
products = Product.objects.all()
for product in products:
    print(product.category.name)  # Query ke DB setiap iterasi!

# ✅ GOOD - Select Related (Foreign Key)
products = Product.objects.select_related('category').all()

# ✅ GOOD - Prefetch Related (Reverse Foreign Key)
categories = Category.objects.prefetch_related('products_set').all()

# ✅ GOOD - Filter di database, bukan di Python
expensive_products = Product.objects.filter(price__gt=100000)  # Di DB
# JANGAN:
expensive_products = [p for p in Product.objects.all() if p.price > 100000]
```

### Caching Strategy:

```python
# Cache hasil yang expensive
@cache_page(60 * 5)  # 5 menit
def get_dashboard_data(request):
    return render(request, 'dashboard.html', {
        'summary': get_sales_summary(),
    })

# Manual cache untuk logic kompleks
def get_top_products():
    cache_key = 'top_products'
    result = cache.get(cache_key)
    if result is None:
        result = Product.objects.annotate(
            sales_count=Count('transactions')
        ).order_by('-sales_count')[:10]
        cache.set(cache_key, result, 3600)  # 1 hour
    return result
```

### Pagination untuk Large Datasets:

```python
from rest_framework.pagination import PageNumberPagination

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

# Gunakan di ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination
```

---

## 📊 Monitoring & Troubleshooting

### Health Check Endpoint:

**File: `lumra_config/views.py`**
```python
from django.http import JsonResponse
from django.core.cache import cache
from django.db import connection
import redis

def health_check(request):
    """Check kesehatan seluruh sistem"""
    health = {
        'status': 'ok',
        'checks': {}
    }
    
    # Check Database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health['checks']['database'] = 'ok'
    except:
        health['checks']['database'] = 'error'
        health['status'] = 'degraded'
    
    # Check Redis/Cache
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        health['checks']['cache'] = 'ok'
    except:
        health['checks']['cache'] = 'error'
        health['status'] = 'degraded'
    
    # Check Celery
    try:
        from celery_app.celery import app
        stats = app.control.inspect().stats()
        health['checks']['celery'] = 'ok' if stats else 'warning'
    except:
        health['checks']['celery'] = 'error'
    
    return JsonResponse(health)
```

### Monitoring Metrics:

```bash
# Prometheus metrics tersedia di:
http://localhost:8000/metrics/

# Pantau dengan Grafana:
# Import dashboard preset untuk Django
```

### Common Issues & Solutions:

| Issue | Cause | Solution |
|-------|-------|----------|
| Redis connection error | Redis server not running | `redis-server` or `redis-cli` |
| Celery tasks stuck | Worker crash | Restart celery worker |
| Slow queries | Missing indexes | Use `django-silk` untuk profiling |
| Out of memory | Cache growing unbounded | Set cache timeout & implement eviction |
| WebSocket 403 error | CSRF token issue | Add `hx-boost` ke HTMX requests |

---

## 🚀 Next Steps

1. **Setup CI/CD** (GitHub Actions, GitLab CI)
   - Auto-test setiap commit
   - Auto-deploy ke staging/production

2. **Load Testing**
   - Gunakan Apache JMeter atau Locust
   - Test dengan 100k concurrent users

3. **Database Partitioning**
   - Implementasikan untuk tabel 10M+ rows
   - Partition berdasarkan date/time

4. **Kubernetes Deployment**
   - Gunakan Helm charts
   - Implement auto-scaling

5. **Advanced Security**
   - WAF (Web Application Firewall)
   - DDoS protection
   - Penetration testing

---

## 📚 Referensi & Resources

- [Django Best Practices](https://docs.djangoproject.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis for Caching](https://redis.io/topics/client-side-caching)
- [MeiliSearch Guide](https://docs.meilisearch.com/)

---

## 💬 Support & Questions

Untuk troubleshooting, cek:
- `logs/lumra.log` untuk application logs
- `logs/lumra_json.log` untuk structured logs
- Sentry dashboard untuk error tracking
- Django Debug Toolbar untuk SQL analysis

Happy coding! 🎉
