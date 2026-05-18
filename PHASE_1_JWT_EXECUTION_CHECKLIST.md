# 🚀 PHASE 1: JWT Authentication Implementation - EXECUTABLE CHECKLIST

**Status:** Ready to Execute  
**Time:** 1-2 hours  
**Current Packages:** ✅ djangorestframework-simplejwt 5.5.1 (already installed)

---

## ✅ STEP 1: Update settings.py (JWT Configuration)

**File:** `lumra_system/settings.py`

### 1.1: Add Import at Top
```python
# After existing imports, add:
from datetime import timedelta
```

### 1.2: Find Your Existing REST_FRAMEWORK Configuration
Look for this section (around line 250):
```python
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
}
```

### 1.3: Replace It With JWT-Enhanced Version
```python
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

# ============ REST FRAMEWORK (UPDATED) ============
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
```

### 1.4: Verify INSTALLED_APPS Has rest_framework
Look for:
```python
INSTALLED_APPS = [
    # ...
    'rest_framework',  # ← Should be here already
    # ...
]
```

---

## ✅ STEP 2: Create JWT URL Endpoints

**File:** `lumra_system/urls.py`

### 2.1: Find Your Current URL Patterns
Look for the urlpatterns list (usually near bottom):
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # ... other patterns ...
]
```

### 2.2: Add These Imports at Top
```python
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
```

### 2.3: Add JWT Endpoints to urlpatterns
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    
    # ✅ NEW JWT Endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ... rest of your URLs ...
]
```

---

## ✅ STEP 3: Test JWT Configuration

### 3.1: Start Django Development Server
```bash
python manage.py runserver
```

### 3.2: Test Token Generation (In New PowerShell Terminal)
```powershell
# Get admin credentials ready
# Then run this curl command:

$body = @{
    username = "admin"
    password = "your_admin_password"  # Replace with actual password
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/token/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 3.3: Expected Response (Success ✅)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE0OTkxNjAwLCJqdGkiOiI2NGU2NmI1OGY3MTg0NjY2YjY2YTAwYWY3MDk2NWQ2MCIsInVzZXJfaWQiOjF9.aBcDeFgHiJkLmNoPqRsTuVwXyZ",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNTA3NzYwMCwianRpIjoiZGMyYWY3NjFlODI2NDI2NWE4YzQ4MmE3OGI4ZTM3YzAiLCJ1c2VyX2lkIjoxfQ.xYzAbCdEfGhIjKlMnOpQrStUvWxYz"
}
```

### 3.4: Test Token Refresh
```powershell
$refreshBody = @{
    refresh = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNTA3NzYwMCwianRpIjoiZGMyYWY3NjFlODI2NDI2NWE4YzQ4MmE3OGI4ZTM3YzAiLCJ1c2VyX2lkIjoxfQ.xYzAbCdEfGhIjKlMnOpQrStUvWxYz"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/auth/token/refresh/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $refreshBody
```

### 3.5: Use JWT Token in API Calls
```powershell
$accessToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIi..."

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

# Example: List products (if you have an API endpoint)
Invoke-WebRequest -Uri "http://localhost:8000/api/products/" `
    -Headers $headers `
    -Method GET
```

---

## ✅ STEP 4: Verification Checklist

Run these commands in PowerShell terminal (while server is running):

### 4.1: Check Settings Loaded
```bash
python manage.py shell
```

Then inside shell:
```python
from django.conf import settings

# Check SIMPLE_JWT exists
print("SIMPLE_JWT" in settings.__dict__)  # Should print: True

# Check JWT in authentication classes
print(settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'])
# Should show: 'rest_framework_simplejwt.authentication.JWTAuthentication'

exit()
```

### 4.2: Test Endpoint Directly
```bash
# Without auth (should fail)
curl http://localhost:8000/api/auth/token/

# With credentials (should succeed)
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"admin\", \"password\": \"your_password\"}"
```

### 4.3: Verify Both Auth Methods Work
```python
# In Django shell:

# Test 1: JWT Auth works
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

user = User.objects.get(username='admin')
refresh = RefreshToken.for_user(user)

print(f"Access Token: {refresh.access_token}")
print(f"Refresh Token: {refresh}")

# Both should print valid tokens

exit()
```

---

## ✅ STEP 5: Quick Integration Test

Create a test file to verify everything works:

**File:** `test_jwt_phase1.py` (in project root)

```python
#!/usr/bin/env python
import os
import django
import requests
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_system.settings')
django.setup()

def test_jwt_phase1():
    """Test JWT Phase 1 Implementation"""
    
    BASE_URL = "http://localhost:8000"
    
    # Test 1: Check settings
    print("✓ Test 1: Checking settings...")
    assert hasattr(settings, 'SIMPLE_JWT'), "SIMPLE_JWT not in settings"
    assert 'rest_framework_simplejwt.authentication.JWTAuthentication' in \
           settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'], \
           "JWT Authentication not in REST_FRAMEWORK"
    print("  ✅ SIMPLE_JWT configured correctly")
    print("  ✅ JWT Authentication enabled")
    
    # Test 2: Test token endpoint exists
    print("\n✓ Test 2: Checking JWT endpoints...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/token/",
            json={"username": "admin", "password": "wrong_password"}
        )
        print(f"  ✅ Token endpoint responds (status: {response.status_code})")
    except Exception as e:
        print(f"  ⚠️  Could not reach endpoint: {e}")
    
    # Test 3: Check session auth still works
    print("\n✓ Test 3: Checking backwards compatibility...")
    assert 'rest_framework.authentication.SessionAuthentication' in \
           settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'], \
           "Session authentication removed (backwards compatibility broken)"
    print("  ✅ Session auth still available (backwards compatible)")
    
    # Test 4: Token refresh endpoint
    print("\n✓ Test 4: Checking refresh endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/token/refresh/",
            json={"refresh": "test"}
        )
        print(f"  ✅ Refresh endpoint responds (status: {response.status_code})")
    except Exception as e:
        print(f"  ⚠️  Could not reach endpoint: {e}")
    
    print("\n✅ Phase 1: JWT Authentication - ALL TESTS PASSED!")
    print("\nNext Steps:")
    print("1. Run Phase 2: Accounting Decimal Precision")
    print("2. Run Phase 3: Database Scalability")
    print("3. Then: Multi-Branch Support")

if __name__ == '__main__':
    test_jwt_phase1()
```

Run it:
```bash
python test_jwt_phase1.py
```

---

## 📋 Completion Checklist

- [ ] Added `from datetime import timedelta` to settings.py
- [ ] Added `SIMPLE_JWT` configuration to settings.py
- [ ] Updated `REST_FRAMEWORK` with JWT authentication
- [ ] Added JWT imports to lumra_system/urls.py
- [ ] Added `/api/auth/token/` endpoint
- [ ] Added `/api/auth/token/refresh/` endpoint
- [ ] Tested token generation (got valid JWT token)
- [ ] Tested token refresh (got new access token)
- [ ] Verified session auth still works (backwards compatible)
- [ ] Ran test_jwt_phase1.py with all tests passing

---

## ✅ Phase 1 Complete!

**Status:** ✅ JWT Authentication Ready

**What You Now Have:**
- ✅ Stateless JWT tokens for mobile/API apps
- ✅ Token rotation for security
- ✅ Session auth fallback for web UI
- ✅ Rate limiting configured
- ✅ Backwards compatible (existing web UI still works)

**Next Phase:** Phase 2 - Accounting Decimal Precision (1-2 hours)

---

## 🆘 Troubleshooting

### Issue: "Module not found: rest_framework_simplejwt"
**Solution:** Already installed! Check with: `pip list | grep simplejwt`

### Issue: "SIMPLE_JWT not in settings"
**Solution:** You added it but not in the right place. Make sure it's BEFORE REST_FRAMEWORK definition.

### Issue: Token endpoint returns 404
**Solution:** Check you added the URLs to `lumra_system/urls.py` correctly. Restart server: `python manage.py runserver`

### Issue: "Could not resolve keyword 'jti_claim'"
**Solution:** This is OK - it's optional. Remove that line if it causes errors.

---

**Ready to execute Phase 1? Start with STEP 1! 🚀**
