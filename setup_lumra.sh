#!/bin/bash

# ============================================================================
# LUMRA DJANGO - SETUP SCRIPT
# ============================================================================
# Script ini akan setup complete development environment untuk Lumra
# Usage: bash setup_lumra.sh
# ============================================================================

set -e  # Exit on error

echo "🚀 Starting Lumra Django Setup..."
echo "=================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ============ Check Prerequisites ============
log_info "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { log_error "Python 3 is required but not installed."; exit 1; }
log_success "Python 3 found: $(python3 --version)"

command -v pip >/dev/null 2>&1 || { log_error "pip is required but not installed."; exit 1; }
log_success "pip found: $(pip --version)"

command -v git >/dev/null 2>&1 || { log_error "Git is required but not installed."; exit 1; }
log_success "Git found: $(git --version)"

# ============ Setup Python Virtual Environment ============
log_info "Setting up Python virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_warning "Virtual environment already exists, skipping creation"
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
log_success "Virtual environment activated"

# ============ Upgrade pip, setuptools, wheel ============
log_info "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel >/dev/null 2>&1
log_success "pip, setuptools, and wheel upgraded"

# ============ Install Dependencies ============
log_info "Installing Python dependencies from requirements.txt..."

if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt not found!"
    exit 1
fi

pip install -r requirements.txt
log_success "All dependencies installed"

# ============ Create .env File ============
log_info "Setting up environment variables..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_success ".env file created from .env.example"
        log_warning "Please update .env file with your configuration"
    else
        log_error ".env.example not found!"
        exit 1
    fi
else
    log_warning ".env file already exists, skipping"
fi

# ============ Create Required Directories ============
log_info "Creating required directories..."

mkdir -p logs
mkdir -p lumra_config/static/css
mkdir -p lumra_config/static/js
mkdir -p lumra_config/static/images
mkdir -p lumra_config/templates
mkdir -p media
mkdir -p db_init

log_success "Directories created"

# ============ Django Setup ============
log_info "Setting up Django..."

# Check if settings.py exists
if [ ! -f "lumra_system/settings.py" ]; then
    if [ -f "settings_production.py" ]; then
        cp settings_production.py lumra_system/settings.py
        log_warning "settings.py created from settings_production.py - update DATABASE config!"
    else
        log_error "settings_production.py not found!"
        exit 1
    fi
else
    log_warning "settings.py already exists, skipping"
fi

# Run migrations
log_info "Running Django migrations..."
python manage.py makemigrations || true
python manage.py migrate
log_success "Migrations completed"

# Collect static files
log_info "Collecting static files..."
python manage.py collectstatic --noinput
log_success "Static files collected"

# ============ Install Pre-commit Hooks ============
log_info "Setting up pre-commit hooks..."

if [ -f ".pre-commit-config.yaml" ]; then
    pip install pre-commit >/dev/null 2>&1
    pre-commit install
    log_success "Pre-commit hooks installed"
else
    log_warning ".pre-commit-config.yaml not found, skipping pre-commit setup"
fi

# ============ Create Superuser ============
log_info "Creating superuser..."

read -p "Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
    log_success "Superuser created"
else
    log_warning "Skipping superuser creation"
fi

# ============ External Services Check ============
log_info "Checking external services..."

# Check PostgreSQL
if command -v psql >/dev/null 2>&1; then
    log_success "PostgreSQL found"
else
    log_warning "PostgreSQL not installed. Please install and configure:"
    echo "  Windows: https://www.postgresql.org/download/windows/"
    echo "  Linux: sudo apt-get install postgresql postgresql-contrib"
    echo "  macOS: brew install postgresql"
fi

# Check Redis
if command -v redis-cli >/dev/null 2>&1; then
    log_success "Redis found"
else
    log_warning "Redis not installed. Please install:"
    echo "  Windows: https://github.com/microsoftarchive/redis/releases"
    echo "  Linux: sudo apt-get install redis-server"
    echo "  macOS: brew install redis"
fi

# ============ Summary ============
echo ""
echo "=================================="
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Start PostgreSQL and Redis:"
echo "   - Linux/macOS: redis-server &"
echo "   - Windows: Run redis-server.exe"
echo "3. Run development server:"
echo "   python manage.py runserver"
echo "4. Access admin at:"
echo "   http://localhost:8000/admin"
echo "5. Monitor Celery (in separate terminal):"
echo "   celery -A lumra_system worker -l info"
echo ""
echo "Documentation: LUMRA_UPGRADE_GUIDE.md"
echo ""
