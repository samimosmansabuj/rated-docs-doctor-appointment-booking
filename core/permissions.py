from rest_framework.permissions import BasePermission
from core.constants import USER_ROLE_CHOICES

class IsDentist(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == USER_ROLE_CHOICES.DENTIST
        )

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == USER_ROLE_CHOICES.PATIENT
        )

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == USER_ROLE_CHOICES.ADMIN
        )



