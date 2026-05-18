# 🚀 LUMRA DJANGO UPGRADE - QUICK REFERENCE

## 📦 Files Delivered (11 Files)

| File | Purpose | Action |
|------|---------|--------|
| `requirements.txt` | Semua pip packages (100+) | `pip install -r requirements.txt` |
| `settings_production.py` | Production-ready Django settings | Copy ke `lumra_system/settings.py` |
| `.env.example` | Environment variables template | Copy ke `.env` dan update values |
| `Dockerfile` | Docker image untuk app | `docker build -t lumra:latest .` |
| `docker-compose.yml` | Complete stack (Postgres, Redis, Django, etc) | `docker-compose up -d` |
| `nginx.conf` | Reverse proxy & load balancing | Copy ke `/etc/nginx/nginx.conf` |
| `.pre-commit-config.yaml` | Code quality hooks | `pre-commit install` |
| `setup_lumra.sh` | Automated setup (Linux/macOS) | `bash setup_lumra.sh` |
| `setup_lumra.bat` | Automated setup (Windows) | `setup_lumra.bat` |
| `LUMRA_UPGRADE_GUIDE.md` | Detailed implementation guide | 📖 Read for complete documentation |
| `MIGRATION_CHECKLIST.md` | Step-by-step migration plan | ✅ Follow for safe migration |

---

## ⚡ Quick Start (5 Minutes)

### Option 1: Automated Setup (Recommended)

**Linux/macOS:**
```bash
bash setup_lumra.sh
```

**Windows:**
```cmd
setup_lumra.bat
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows

# 2. Upgrade pip
pip install --upgrade pip setuptools wheel

# 3. Install packages
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env dengan konfigurasi Anda

# 5. Django setup
cp settings_production.py lumra_system/settings.py
mkdir -p logs lumra_config/static media

# 6. Run migrations
python manage.py migrate
python manage.py collectstatic --noinput

# 7. Start services
python manage.py runserver
# Di terminal lain:
celery -A lumra_system worker -l info
celery -A lumra_system beat -l info
```

### Option 3: Docker Compose (Production)

```bash
# Copy .env dan update values
cp .env.example .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec django python manage.py migrate

# Check status
docker-compose ps
```

---

## 🔑 Configuration Checklist

### Minimal Setup (untuk jalan)
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DB_HOST=localhost
REDIS_URL=redis://127.0.0.1:6379/1
```

### Full Production Setup
```env
# Lihat .env.example untuk semua 70+ options
# Update yang penting:
- SECRET_KEY (jangan gunakan default!)
- DATABASE credentials
- REDIS URL
- SENTRY_DSN (untuk error tracking)
- EMAIL configuration
- CORS settings
- SSL/TLS flags (untuk production)
```

---

## 📊 Package Breakdown (100+ Packages)

### Core Django (5)
- Django 6.0, DRF, PostgreSQL adapter, Extensions, Browser reload

### UI/Frontend (6)
- Unfold, Tailwind, Crispy Forms, Alpine.js, HTMX, Widget tweaks

### Database Optimization (4)
- django-pg-indexes, django-cacheops, redis, django-cachalot

### Background Tasks (5)
- Celery, Celery Beat, Kombu, Vine, RabbitMQ compatibility

### Real-time Updates (2)
- Django Channels, Channels Redis

### Search & Analytics (3)
- MeiliSearch, Elasticsearch, JSON logging

### Monitoring (4)
- Sentry, Prometheus, Django Silk, python-json-logger

### Security (4)
- django-axes, django-csp, python-decouple, HTTPS support

### Testing (6)
- pytest, pytest-django, pytest-cov, faker, factory-boy, coverage

### Code Quality (4)
- black, ruff, isort, flake8, pre-commit

### Additional (20+)
- PDF generation, Excel export, Email, CORS, Documentation tools, etc.

---

## 🚀 Common Commands

### Development
```bash
# Start Django development server
python manage.py runserver

# Start Celery worker (background tasks)
celery -A lumra_system worker -l info

# Start Celery beat (scheduled tasks)
celery -A lumra_system beat -l info

# Run Django shell
python manage.py shell

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Check project health
python manage.py check
python manage.py check --deploy

# Create superuser
python manage.py createsuperuser
```

### Database
```bash
# Connect to PostgreSQL
python manage.py dbshell

# Backup database
pg_dump lumra_set_allegra > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql lumra_set_allegra < backup_file.sql

# Clear cache
python manage.py shell
from django.core.cache import cache
cache.clear()
```

### Docker
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs django
docker-compose logs celery_worker
docker-compose logs postgres

# Run migrations in container
docker-compose exec django python manage.py migrate

# Access Django shell in container
docker-compose exec django python manage.py shell
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lumra_config

# Run specific test
pytest tests/test_models.py

# Run slow tests report
pytest --durations=10
```

### Code Quality
```bash
# Format code with black
black .

# Sort imports
isort .

# Lint with ruff
ruff check . --fix

# Type checking
mypy lumra_config

# All checks together (pre-commit)
pre-commit run --all-files
```

---

## 🔗 Service URLs (Development)

| Service | URL | Notes |
|---------|-----|-------|
| Django App | http://localhost:8000 | Main application |
| Admin | http://localhost:8000/admin | Unfold admin interface |
| API Docs | http://localhost:8000/api/schema/swagger-ui/ | OpenAPI schema |
| ReDoc | http://localhost:8000/api/schema/redoc/ | Alternative API docs |
| Prometheus | http://localhost:8000/metrics/ | Metrics for Grafana |
| Silk | http://localhost:8000/silk/ | Request profiling |
| Health Check | http://localhost:8000/health/ | System health status |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache & message broker |
| MeiliSearch | http://localhost:7700 | Search engine admin |

---

## 🔐 Security Essentials

### Before Going to Production
- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Setup SSL certificates
- [ ] Enable HTTPS redirect
- [ ] Configure CSRF trusted origins
- [ ] Setup database backups
- [ ] Configure monitoring (Sentry)
- [ ] Enable rate limiting
- [ ] Setup firewall rules
- [ ] Review security headers
- [ ] Test security with `python manage.py check --deploy`

### Security Headers Added
```
Strict-Transport-Security: max-age=31536000
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: [configured]
```

---

## 📈 Performance Optimization Features

### Database
- ✅ Connection pooling (PgBouncer)
- ✅ Query optimization (select_related, prefetch_related)
- ✅ Indexes (BTree, GIN, BRIN)
- ✅ Partitioning support
- ✅ Materialized views

### Caching
- ✅ Redis query result caching
- ✅ Cachalot automatic invalidation
- ✅ Session caching
- ✅ Template caching

### Search
- ✅ MeiliSearch full-text search
- ✅ Instant autocomplete
- ✅ Typo-tolerant search

### Background Tasks
- ✅ Heavy computation in Celery
- ✅ Scheduled jobs with Beat
- ✅ Result tracking
- ✅ Retry logic

### Monitoring
- ✅ Error tracking (Sentry)
- ✅ Metrics collection (Prometheus)
- ✅ JSON structured logging
- ✅ Request profiling (Silk)

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| ImportError for package | `pip install -r requirements.txt` |
| Database connection error | Check PostgreSQL running, credentials in .env |
| Redis connection error | Check Redis running: `redis-cli ping` |
| Celery tasks stuck | Restart: `celery -A lumra_system worker -l info` |
| Static files 404 | Run: `python manage.py collectstatic --noinput` |
| CSRF token error | Check CSRF_TRUSTED_ORIGINS in settings |
| WebSocket 403 | Check channels config, Redis connection |
| Slow queries | Use `django-silk` profiling tool |
| Out of memory | Reduce cache timeout, implement eviction policy |

---

## 📚 Documentation

1. **LUMRA_UPGRADE_GUIDE.md** - Complete implementation guide
   - Architecture overview
   - Setup instructions
   - Component configuration
   - Best practices
   - Monitoring setup

2. **MIGRATION_CHECKLIST.md** - Step-by-step migration plan
   - 10 phases
   - Backup procedures
   - Testing procedures
   - Security hardening
   - Go-live checklist

3. **This file** - Quick reference

---

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Documentation](https://redis.io/documentation)
- [MeiliSearch Guide](https://docs.meilisearch.com/)
- [Docker Documentation](https://docs.docker.com/)

---

## 💡 Pro Tips

1. **Start with Docker Compose** - Simplest way to get everything running
2. **Read LUMRA_UPGRADE_GUIDE.md completely** - Saves debugging time later
3. **Use pre-commit hooks** - Prevent bad code from being committed
4. **Monitor from day 1** - Setup Sentry early
5. **Test database backups** - Restore them regularly
6. **Profile slow queries** - Use django-silk before optimization
7. **Keep logs structured** - JSON logging for easier analysis
8. **Document your customizations** - Future you will thank present you

---

## 🆘 Need Help?

- Check logs: `logs/lumra.log` dan `logs/lumra_json.log`
- Docker logs: `docker-compose logs [service]`
- Django check: `python manage.py check --deploy`
- Health endpoint: `curl http://localhost:8000/health/`
- Database health: `python manage.py dbshell` then `SELECT 1;`
- Redis health: `redis-cli ping` (should return PONG)

---

## ✨ Next Steps After Setup

1. ✅ Run migrations
2. ✅ Create superuser
3. ✅ Collect static files
4. ✅ Configure email
5. ✅ Setup Sentry
6. ✅ Setup scheduled tasks (Celery Beat)
7. ✅ Configure backups
8. ✅ Setup monitoring dashboard (Grafana + Prometheus)
9. ✅ Load test the system
10. ✅ Deploy to production

---

**Version:** 2.0.0  
**Last Updated:** 2024-01-05  
**Environment:** Production-Ready  

Happy deploying! 🚀
