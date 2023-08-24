from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Normal users and anonymous have access only with
    GET, HEAD or OPTION requests. Admins have full access."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff