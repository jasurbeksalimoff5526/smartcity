from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


def has_role(user, *roles):
    return user.is_authenticated and (user.is_superuser or user.role in roles)


def role_required(*roles):
    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            if has_role(request.user, *roles):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return wrapped

    return decorator


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        return has_role(self.request.user, *self.allowed_roles)
