# 📋 MIGRATION CHECKLIST - Lumra Django Upgrade

## 🎯 Phase 1: Pre-Migration (Persiapan)

### 1.1 Backup Existing Project
- [ ] Backup database PostgreSQL
  ```bash
  pg_dump lumra_set_allegra > backup_$(date +%Y%m%d_%H%M%S).sql
  ```
- [ ] Backup file requirements.txt
- [ ] Backup settings.py
- [ ] Backup entire project directory
- [ ] Create git branch untuk migration
  ```bash
  git checkout -b feature/production-upgrade
  ```

### 1.2 Review Existing Configuration
- [ ] Catat current INSTALLED_APPS
- [ ] Catat current MIDDLEWARE
- [ ] Review custom settings atau environment variables
- [ ] List semua third-party packages yang sudah installed
- [ ] Check compatibility dengan Python 3.11+

### 1.3 Prepare Development Environment
- [ ] Install Git (jika belum)
- [ ] Install PostgreSQL 13+ (jika belum)
- [ ] Install Redis (jika belum)
- [ ] Install Node.js (untuk npm, optional untuk Tailwind)
- [ ] Create Python 3.11 virtual environment baru

---

## 🔧 Phase 2: Installation & Configuration

### 2.1 Install New Requirements
```bash
# Backup old requirements
cp requirements.txt requirements.backup.txt

# Install dari requirements.txt yang baru
pip install -r requirements.txt

# Verify installation
pip list | grep -E "Django|celery|redis|postgres"
```

- [ ] All packages installed successfully
- [ ] No version conflicts
- [ ] Check pip list untuk installed packages

### 2.2 Update Django Settings
```bash
# Backup old settings
cp lumra_system/settings.py lumra_system/settings.old.py

# Copy new settings
cp settings_production.py lumra_system/settings.py
```

- [ ] Review INSTALLED_APPS di new settings
- [ ] Update DATABASE configuration
- [ ] Update SECRET_KEY di production
- [ ] Configure Redis connections
- [ ] Configure Celery settings

### 2.3 Setup Environment Variables
```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dengan values yang benar
nano .env  # atau editor lain
```

Update fields:
- [ ] SECRET_KEY - generate baru untuk production
- [ ] DEBUG=False untuk production
- [ ] Database credentials
- [ ] Redis URL
- [ ] Email configuration
- [ ] Sentry DSN (optional)
- [ ] CORS settings

### 2.4 Create Required Directories
```bash
mkdir -p logs
mkdir -p lumra_config/static
mkdir -p media
mkdir -p db_init
```
- [ ] All directories created

### 2.5 Install Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```
- [ ] Pre-commit hooks installed
- [ ] Run linter & formatter terhadap existing code

---

## 🗄️ Phase 3: Database Migrations & Setup

### 3.1 Run Django Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --run-syncdb
```
- [ ] All migrations ran successfully
- [ ] No migration errors

### 3.2 Collect Static Files
```bash
python manage.py collectstatic --noinput
```
- [ ] Static files collected to STATIC_ROOT

### 3.3 Create Superuser
```bash
python manage.py createsuperuser
```
- [ ] Superuser created dengan credentials aman

### 3.4 Verify Database Structure
```bash
python manage.py dbshell
```
SQL checks:
- [ ] Tabel users intact
- [ ] Tabel django_session healthy
- [ ] Foreign keys valid
- [ ] Indexes present

---

## 🚀 Phase 4: Testing & Verification

### 4.1 Run Unit Tests
```bash
pytest --cov=lumra_config
# atau
python manage.py test
```
- [ ] All tests pass
- [ ] Code coverage > 80%

### 4.2 Test Django Management Commands
```bash
python manage.py check  # Check project health
python manage.py shell  # Test Django shell
```
- [ ] `python manage.py check` returns OK
- [ ] No warnings atau errors

### 4.3 Test External Services
```bash
# Test Database
python manage.py dbshell
> SELECT 1;  -- harus return 1
> \q

# Test Redis
redis-cli ping  -- harus return PONG
redis-cli flushall  -- clear cache
```
- [ ] PostgreSQL connection OK
- [ ] Redis connection OK
- [ ] MeiliSearch accessible (jika installed)

### 4.4 Test Django Admin
```bash
python manage.py runserver
# Visit http://localhost:8000/admin
```
- [ ] Login successful
- [ ] Admin interface responsive
- [ ] Database tables visible

### 4.5 Test Celery Tasks
```bash
# Terminal 1: Celery Worker
celery -A lumra_system worker -l info

# Terminal 2: Django shell
python manage.py shell
from lumra_config.tasks import test_task
result = test_task.delay()
print(result.get())  # Should return success
```
- [ ] Celery worker started successfully
- [ ] Task executed
- [ ] Result returned

### 4.6 Performance Testing
```bash
# Test slow queries
python manage.py shell
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    # Your query here
    pass
print(f"Queries: {len(ctx)}, Time: {ctx.execution_time}")
```
- [ ] No N+1 queries
- [ ] Query time < 500ms

### 4.7 Security Checks
```bash
python manage.py check --deploy
```
- [ ] All security checks pass
- [ ] DEBUG=False di production
- [ ] ALLOWED_HOSTS configured
- [ ] CSRF settings correct

---

## 🐳 Phase 5: Docker & Production Deployment

### 5.1 Build Docker Image (Optional)
```bash
docker build -t lumra:latest .
```
- [ ] Docker image built successfully
- [ ] No build errors

### 5.2 Docker Compose Setup
```bash
docker-compose up -d
docker-compose ps  # Check all services running
```
- [ ] PostgreSQL service running
- [ ] Redis service running
- [ ] MeiliSearch service running (jika enabled)
- [ ] Django service running
- [ ] Celery worker running
- [ ] Celery beat running

### 5.3 Verify Docker Containers
```bash
docker-compose logs django  # Check Django logs
docker-compose logs postgres  # Check PostgreSQL logs
docker-compose logs redis  # Check Redis logs
```
- [ ] No error logs
- [ ] Services healthy

### 5.4 Database Migrations in Docker
```bash
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
docker-compose exec django python manage.py collectstatic --noinput
```
- [ ] All migrations ran
- [ ] Superuser created
- [ ] Static files collected

---

## 🔒 Phase 6: Security Hardening

### 6.1 Secret Management
- [ ] Change SECRET_KEY dari default
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- [ ] Use environment variables, bukan hardcoded
- [ ] Store sensitive data di .env, not in code
- [ ] Add .env ke .gitignore

### 6.2 Security Headers
- [ ] SECURE_SSL_REDIRECT = True (production)
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] SECURE_HSTS_SECONDS = 31536000
- [ ] X-Frame-Options = SAMEORIGIN
- [ ] X-Content-Type-Options = nosniff

### 6.3 Database Security
- [ ] Change default PostgreSQL password
- [ ] Enable SSL connections untuk database
- [ ] Restrict database access to app servers only
- [ ] Regular backups with retention policy

### 6.4 API Security
- [ ] Enable rate limiting
- [ ] Setup CORS properly
- [ ] Implement API authentication (tokens)
- [ ] Validate all inputs

### 6.5 User Authentication
- [ ] Enforce strong passwords (12+ chars)
- [ ] Enable 2FA (optional)
- [ ] Setup fail2ban atau axes untuk brute force
- [ ] Regular password rotation policy

---

## 📊 Phase 7: Monitoring & Logging Setup

### 7.1 Logging Configuration
- [ ] Logs directory created (logs/)
- [ ] Log rotation configured
- [ ] JSON logging enabled
- [ ] Structured logging untuk errors

### 7.2 Error Tracking (Sentry)
```bash
# Setup Sentry if using
pip install sentry-sdk
# Configure SENTRY_DSN di settings.py dan .env
```
- [ ] Sentry account created (jika using)
- [ ] DSN configured
- [ ] Test error sending:
  ```python
  from sentry_sdk import capture_exception
  capture_exception(Exception("Test error"))
  ```

### 7.3 Monitoring & Metrics
- [ ] Prometheus metrics enabled
- [ ] Django-prometheus configured
- [ ] Health check endpoint working
  ```bash
  curl http://localhost:8000/health/
  ```
- [ ] Metrics endpoint accessible
  ```bash
  curl http://localhost:8000/metrics/
  ```

### 7.4 Log Aggregation (Optional)
- [ ] Setup ELK Stack atau Loki (optional)
- [ ] Configure log shipping
- [ ] Test log queries

---

## 🚢 Phase 8: Production Deployment

### 8.1 DNS & Domain Setup
- [ ] Domain registered & pointing to server IP
- [ ] DNS records configured (A, CNAME)
- [ ] SSL certificate obtained (Let's Encrypt)

### 8.2 Server Setup
- [ ] Server OS updated (Ubuntu 22.04 LTS recommended)
- [ ] Firewall configured (only allow 80, 443, 22)
- [ ] SSH key setup (no password login)
- [ ] Fail2ban installed untuk brute force protection

### 8.3 Database Backup Strategy
- [ ] Daily backups automated
  ```bash
  # Cron job untuk backup
  0 2 * * * /home/django/backup_db.sh
  ```
- [ ] Test restore procedure
- [ ] Backup storage redundant (local + cloud)

### 8.4 Nginx Configuration
- [ ] Nginx installed & configured
- [ ] SSL certificates installed
- [ ] Reverse proxy working
- [ ] Gzip compression enabled
- [ ] Rate limiting configured

### 8.5 Process Management
- [ ] Gunicorn/Daphne processes managed by systemd
- [ ] Celery worker managed by systemd
- [ ] Celery beat managed by systemd
- [ ] Auto-restart on failure configured

### 8.6 CI/CD Pipeline (Optional)
- [ ] GitHub Actions / GitLab CI configured
- [ ] Auto-tests on every commit
- [ ] Auto-deploy to staging
- [ ] Manual approval untuk production deploy

### 8.7 Load Testing
```bash
# Gunakan Apache JMeter atau Locust
pip install locust
locust -f locustfile.py
```
- [ ] App handles 100+ concurrent users
- [ ] Response time < 500ms
- [ ] No memory leaks detected
- [ ] Database connection pool healthy

---

## ✅ Phase 9: Go-Live Checklist

### 9.1 Final Verification
- [ ] All tests passing
- [ ] All services running
- [ ] Database healthy
- [ ] Backups working
- [ ] Monitoring active

### 9.2 Stakeholder Notification
- [ ] Team notified tentang go-live
- [ ] Support team trained
- [ ] Rollback plan documented
- [ ] Escalation contacts documented

### 9.3 Launch
- [ ] Run final health checks
- [ ] Switch DNS jika diperlukan
- [ ] Monitor error logs closely
- [ ] Quick response team on standby

### 9.4 Post-Launch Monitoring
- [ ] Check logs setiap 15 menit first hour
- [ ] Check metrics dashboard
- [ ] Monitor error tracking (Sentry)
- [ ] User feedback collection

---

## 🔄 Phase 10: Post-Migration Tasks

### 10.1 Documentation
- [ ] Update API documentation
- [ ] Create runbooks untuk common tasks
- [ ] Document deployment procedures
- [ ] Create disaster recovery plan

### 10.2 Optimization
- [ ] Analyze slow queries
- [ ] Optimize database indexes
- [ ] Review caching strategy
- [ ] Load test & stress test

### 10.3 Cleanup
- [ ] Remove old settings backup files
- [ ] Clean up temporary files
- [ ] Archive old database backups
- [ ] Remove deprecated code

### 10.4 Knowledge Transfer
- [ ] Document system architecture
- [ ] Create training materials
- [ ] Conduct team training
- [ ] Schedule regular knowledge-sharing sessions

---

## 📞 Support & Troubleshooting

### Common Issues:

| Issue | Solution |
|-------|----------|
| ImportError: No module | `pip install -r requirements.txt` |
| Database connection error | Check PostgreSQL running, credentials correct |
| Redis connection error | Check Redis running on correct port |
| Celery tasks stuck | Restart celery worker & purge queue |
| Static files 404 | Run `python manage.py collectstatic` |
| CSRF token mismatch | Check CSRF_TRUSTED_ORIGINS in settings |
| WebSocket 403 | Check channels configuration, Redis connection |

### Useful Commands:

```bash
# Health check
python manage.py check
python manage.py check --deploy

# Database
python manage.py dbshell
python manage.py dumpdata > backup.json

# Cache
python manage.py shell
from django.core.cache import cache
cache.clear()

# Celery
celery -A lumra_system worker --purge
celery -A lumra_system inspect active

# Logs
tail -f logs/lumra.log
tail -f logs/lumra_json.log
```

---

## 🎉 Completion

Once all phases are complete:
- [ ] Send completion report to stakeholders
- [ ] Schedule post-migration review meeting
- [ ] Plan future optimization work
- [ ] Update documentation with lessons learned

**Estimated Timeline:** 
- Development environment: 2-4 hours
- Testing phase: 4-8 hours
- Production deployment: 2-4 hours
- Total: 1-2 days

---

## 📞 Contact & Support

For issues or questions:
- Check LUMRA_UPGRADE_GUIDE.md
- Review logs in `logs/` directory
- Check Docker container logs: `docker-compose logs [service]`
- Ask in team channels or documentation

Good luck! 🚀
