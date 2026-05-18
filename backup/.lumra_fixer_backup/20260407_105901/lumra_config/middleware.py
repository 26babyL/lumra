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
