"""
Permission Decorators for LUMRA

Provides enhanced decorators for views that require specific permissions,
accounting approval, and branch access validation.

Usage:
    from lumra_config.decorators import (
        accounting_permission_required,
        branch_access_required,
        api_accounting_permission,
    )
    
    @accounting_permission_required('change_invoice')
    def edit_invoice(request, invoice_id):
        ...
    
    @api_accounting_permission('create_accounting')
    @api_view(['POST'])
    def create_journal_entry(request):
        ...
"""

from functools import wraps
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
import logging

logger = logging.getLogger(__name__)


# ============ DJANGO VIEW DECORATORS ============

def accounting_permission_required(permission_codename):
    """
    Enhanced permission decorator for accounting operations.
    
    - Requires login
    - Requires specific permission
    - Logs audit trail
    - Validates branch access
    
    Args:
        permission_codename: Permission code like 'change_invoice', 'create_accounting'
    
    Example:
        @accounting_permission_required('change_invoice')
        def edit_invoice(request, invoice_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        @permission_required(f'lumra_config.{permission_codename}', raise_exception=True)
        def wrapper(request, *args, **kwargs):
            # Audit log this action
            try:
                from lumra_config.models import AuditTrail
                AuditTrail.objects.create(
                    user=request.user,
                    action=permission_codename,
                    resource=view_func.__name__,
                    ip_address=_get_client_ip(request),
                )
            except Exception as e:
                logger.error(f"Error creating audit trail: {e}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def branch_access_required(view_func):
    """
    Ensure user has access to requested branch.
    
    Validates that request.GET['branch_id'] or request.POST['branch_id']
    matches one of the user's accessible branches.
    
    Example:
        @branch_access_required
        def view_branch_reports(request):
            branch_id = request.GET.get('branch_id')
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        branch_id = request.GET.get('branch_id') or request.POST.get('branch_id')
        
        if not branch_id:
            raise PermissionDenied('Branch ID required')
        
        # Check if user has access to this branch
        try:
            from lumra_config.models import BranchPermission
            
            has_access = (
                request.user.is_superuser or
                BranchPermission.objects.filter(
                    user=request.user,
                    branch_id=int(branch_id)
                ).exists()
            )
            
            if not has_access:
                logger.warning(
                    f"Branch access denied for user {request.user.id} "
                    f"to branch {branch_id}"
                )
                raise PermissionDenied('Branch access denied')
        
        except (ValueError, TypeError):
            raise PermissionDenied('Invalid branch ID')
        except Exception as e:
            logger.error(f"Error checking branch access: {e}")
            # Fail open in development, closed in production
            from django.conf import settings
            if not getattr(settings, 'DEBUG', False):
                raise
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def accounting_approval_required(view_func):
    """
    Decorator for operations that require accounting manager approval.
    
    Checks if:
    1. User has accounting permission
    2. User is in 'Accounting' group
    
    Example:
        @accounting_approval_required
        def approve_invoice(request, invoice_id):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # Check if user is in Accounting group
        has_permission = (
            request.user.is_superuser or
            request.user.groups.filter(name='Accounting').exists()
        )
        
        if not has_permission:
            logger.warning(
                f"Accounting approval access denied for user {request.user.id}"
            )
            raise PermissionDenied(
                'Only accounting staff can perform this action'
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# ============ REST API PERMISSIONS ============

class IsAccountingStaff(BasePermission):
    """Permission class: User must be in 'Accounting' group"""
    
    message = 'You do not have permission to access this resource.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or
             request.user.groups.filter(name='Accounting').exists())
        )


class IsBranchManager(BasePermission):
    """Permission class: User must be branch manager"""
    
    message = 'Only branch managers can perform this action.'
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.user.is_superuser:
            return True
        
        try:
            # Check if user has branch manager permission
            return request.user.groups.filter(name='Branch Manager').exists()
        except Exception as e:
            logger.error(f"Error checking branch manager permission: {e}")
            return False


class BranchIsolationPermission(BasePermission):
    """
    Permission class: User can only access their branch's data.
    
    Checks that the object's branch_id matches user's accessible branches.
    """
    
    message = 'You do not have access to this branch.'
    
    def has_object_permission(self, request, view, obj):
        # Superusers can access everything
        if request.user.is_superuser:
            return True
        
        # Check if object has branch attribute
        if not hasattr(obj, 'branch_id'):
            return True  # No branch isolation needed for this object
        
        # Check if user has access to this branch
        try:
            from lumra_config.models import BranchPermission
            
            has_access = BranchPermission.objects.filter(
                user=request.user,
                branch_id=obj.branch_id
            ).exists()
            
            return has_access
        except Exception as e:
            logger.error(f"Error checking branch isolation permission: {e}")
            return False


class CanApproveAccounting(BasePermission):
    """
    Permission class: User can approve accounting entries.
    
    Requires:
    - In 'Accounting' group
    - Or is superuser
    """
    
    message = 'You do not have permission to approve accounting entries.'
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        return (
            request.user.is_superuser or
            request.user.groups.filter(name='Accounting').exists()
        )


# ============ REST API DECORATORS ============

def api_accounting_permission(permission_name):
    """
    Decorator for REST API endpoints requiring accounting permission.
    
    Example:
        @api_accounting_permission('create_accounting')
        @api_view(['POST'])
        def create_journal_entry(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not (request.user and request.user.is_authenticated):
                return JsonResponse(
                    {'detail': 'Authentication required'},
                    status=401
                )
            
            # Check if user has permission
            has_permission = (
                request.user.is_superuser or
                request.user.groups.filter(name='Accounting').exists()
            )
            
            if not has_permission:
                logger.warning(
                    f"API accounting permission denied for user "
                    f"{request.user.id} to {permission_name}"
                )
                return JsonResponse(
                    {'detail': 'Permission denied'},
                    status=403
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


# ============ UTILITY FUNCTIONS ============

def _get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
