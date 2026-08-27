from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Autorise uniquement les utilisateurs avec le rôle 'admin'
    (ou le statut is_staff/is_superuser de Django).
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == 'admin' or request.user.is_staff)
        )


class IsCandidate(permissions.BasePermission):
    """
    Autorise uniquement les utilisateurs ayant le rôle 'candidate'.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'candidate'
        )


class IsOrganization(permissions.BasePermission):
    """
    Autorise uniquement les utilisateurs ayant le rôle 'organization'.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'organization'
        )


class IsOwner(permissions.BasePermission):
    """
    Permission au niveau de l'objet : autorise l'accès uniquement
    si l'utilisateur connecté est le propriétaire de l'objet.

    Suppose que l'objet possède un attribut désignant son propriétaire.
    Par défaut cherche 'obj.owner', mais peut être adapté via 'owner_field'
    dans la vue si besoin (ex: 'obj.candidate.user').
    """

    owner_field = 'owner'

    def has_object_permission(self, request, view, obj):
        owner_field = getattr(view, 'owner_field', self.owner_field)
        owner = obj
        for part in owner_field.split('.'):
            owner = getattr(owner, part, None)
            if owner is None:
                return False
        return owner == request.user


class ReadOnly(permissions.BasePermission):
    """
    Autorise uniquement les requêtes en lecture seule (GET, HEAD, OPTIONS).
    Utile combinée à d'autres permissions avec des opérateurs | (OR).
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS