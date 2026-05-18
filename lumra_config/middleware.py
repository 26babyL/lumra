# lumra_config/middleware.py
# Auto-sync dari core/middleware.py oleh lumra_sync.py
# Dibutuhkan oleh templates: user.profile, user.role, user.avatar, dll.
# WAJIB didaftarkan di settings.py → MIDDLEWARE

from django.utils.deprecation import MiddlewareMixin

from lumra_config.models import UserProfile


class EnsureUserProfileMiddleware(MiddlewareMixin):
    """Middleware that makes sure authenticated users always have a profile.

    The templates throughout the project assume ``user.profile`` is available
    (see ``products.html``, ``navbar.html`` etc.).  If a ``User`` has no
    ``UserProfile`` row yet the reverse accessor doesn't exist, which leads to
    ``VariableDoesNotExist`` errors like the one seen at
    ``/inventory/products/``.  This middleware runs after
    ``AuthenticationMiddleware`` and creates a profile on-the-fly when
    necessary, then attaches it to ``request.user`` so that ``user.profile``
    lookup always succeeds.

    Creating the profile here has the additional benefit that subsequent
    views/endpoints can safely assume ``request.user.profile`` exists without
    having to call ``get_or_create`` themselves.
    """

    # TODO[C3-LONG]: 'process_request' = 70 baris (max 30). Pecah: process_request_validate(), process_request_query(), process_request_render()
    # TODO[C3-LONG]: 'process_request' terlalu panjang (70 baris). Pecah: process_request_validate(), process_request_build_context(), process_request_render()
    # TODO[C3-LONG]: 'process_request' = 71 baris (maks 30). Pecah: process_request_validate(), process_request_process(), process_request_respond()
    def process_request(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            # ``get_or_create`` will return the existing profile if one
            # already exists, otherwise it'll make a new row in the database.
            profile, _ = UserProfile.objects.get_or_create(user=user)

            # attach attribute for ease-of-use in templates and code
            setattr(user, "profile", profile)

            # lots of templates assume certain attributes exist on the
            # profile object (avatar, role, phone, etc.).  the actual
            # ``UserProfile`` model in this project only has a
            # ``location`` field, so we supply in-memory defaults here to
            # prevent missing-key errors during template rendering.  None of
            # these values are saved to the database.
            defaults = {
                "role": "User",
                "phone": "",
                "address": "",
                "two_factor_enabled": False,
                "language": "id",
                "email_notifications": False,
                "push_notifications": False,
                "marketing_emails": False,
                "theme": "light",
            }

            for attr, val in defaults.items():
                if not hasattr(profile, attr):
                    setattr(profile, attr, val)

            # avatar is expected to be an object with a ``url`` property.
            if not hasattr(profile, "avatar") or profile.avatar is None:
                from types import SimpleNamespace
                setattr(profile, "avatar", SimpleNamespace(url="/static/img/default-avatar.png"))

            # ``stores`` is iterated with ``.all`` in several templates.
            if not hasattr(profile, "stores"):
                class _DummyManager:
                    def all(self):
                        return []
                setattr(profile, "stores", _DummyManager())
            # inject reasonable defaults for attributes that are assumed by
            # the templates but are not actual database fields on the
            # minimal ``UserProfile`` model.  this avoids repeated
            # ``VariableDoesNotExist``/AttributeError errors when a fresh
            # profile row is created with only the "location" field.
            defaults = {
                'role': 'User',
                'avatar': None,
                'phone': '',
                'address': '',
                'two_factor_enabled': False,
                'language': 'id',
                'email_notifications': False,
                'push_notifications': False,
                'marketing_emails': False,
                'theme': 'light',
            }
            for attr, val in defaults.items():
                if not hasattr(profile, attr):
                    setattr(profile, attr, val)
            # ``stores`` property is iterated in several templates; supply a
            # dummy object with an ``all()`` method returning an empty list.
            if not hasattr(profile, 'stores'):
                class _EmptyManager(list):
                    def all(self_inner):
                        return []
                profile.stores = _EmptyManager()
        # no return value needed; Django continues processing as usual


# ============ NEW: BRANCH ISOLATION MIDDLEWARE ============

import logging
from django.http import HttpResponseForbidden
from django.conf import settings

logger = logging.getLogger(__name__)


class BranchIsolationMiddleware(MiddlewareMixin):
    """
    Enforce branch-level data isolation for multi-branch systems (32 branches).
    
    - Extracts branch_id from request parameters or session
    - Validates user has access to requested branch
    - Sets request.current_branch_id for use in views
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.multi_branch_enabled = getattr(
            settings,
            'MULTI_BRANCH_CONFIG',
            {}
        ).get('ENABLED', False)
    
    def process_request(self, request):
        # Only apply if multi-branch is enabled
        if self.multi_branch_enabled and request.user.is_authenticated:
            branch_id = self._get_requested_branch(request)
            
            # Validate access
            if not self._has_branch_access(request.user, branch_id):
                logger.warning(
                    f"Branch access denied for user {request.user.id} "
                    f"to branch {branch_id}"
                )
                return HttpResponseForbidden('Branch access denied')
            
            # Set in request context for use in views
            request.current_branch_id = branch_id
            request.session['current_branch_id'] = branch_id
        
        return None  # Continue processing
    
    def _get_requested_branch(self, request):
        """Extract branch_id from request or session"""
        # Priority: GET param > POST param > Session > Default
        branch_id = (
            request.GET.get('branch_id') or
            request.POST.get('branch_id') or
            request.session.get('current_branch_id') or
            getattr(
                settings,
                'MULTI_BRANCH_CONFIG',
                {}
            ).get('DEFAULT_BRANCH_ID', 1)
        )
        try:
            return int(branch_id)
        except (ValueError, TypeError):
            return 1
    
    def _has_branch_access(self, user, branch_id):
        """Check if user has access to this branch"""
        # Skip for superusers
        if user.is_superuser:
            return True
        
        # Check if user has access
        try:
            from lumra_config.models import BranchPermission
            
            has_access = BranchPermission.objects.filter(
                user=user,
                branch_id=branch_id
            ).exists()
            
            return has_access
        except Exception as e:
            logger.error(f"Error checking branch access: {e}")
            # Fail open in development, closed in production
            return getattr(settings, 'DEBUG', False)


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Log all important actions for audit trail.
    
    Captures:
    - Who (user_id)
    - What (request method, path)
    - When (timestamp)
    - Status (response code)
    """
    
    # Paths that should NOT be audited
    EXCLUDE_PATHS = [
        '/static/',
        '/media/',
        '/api/health/',
        '/api/metrics/',
        '/admin/jsi18n/',
    ]
    
    # Only audit these methods
    AUDIT_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def process_request(self, request):
        # Check if we should audit this request
        should_audit = (
            self._should_audit(request) and
            request.user.is_authenticated
        )
        
        if should_audit:
            request._audit_start = True
        
        return None
    
    def process_response(self, request, response):
        if getattr(request, '_audit_start', False):
            self._log_audit(request, response)
        
        return response
    
    def _should_audit(self, request):
        """Check if request should be audited"""
        # Check method
        if request.method not in self.AUDIT_METHODS:
            return False
        
        # Check if path is excluded
        for exclude_path in self.EXCLUDE_PATHS:
            if request.path.startswith(exclude_path):
                return False
        
        return True
    
    def _log_audit(self, request, response):
        """Log audit entry"""
        try:
            from lumra_config.models import AuditTrail
            
            AuditTrail.objects.create(
                user=request.user,
                action=request.method,
                resource=request.path,
                status_code=response.status_code,
                ip_address=self._get_client_ip(request),
            )
        except Exception as e:
            logger.error(f"Error logging audit trail: {e}")
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
