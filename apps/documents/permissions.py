# apps/documents/permissions.py
# C:\optimumjobs-backend\apps\documents\permissions.py

from rest_framework import permissions


class IsDocumentOwner(permissions.BasePermission):
    """
    Permission qui permet :
    - Le propriétaire du document
    - Les administrateurs
    - Les organisations (via les candidatures)
    """
    def has_object_permission(self, request, view, obj):
        # ✅ 1. Le propriétaire peut accéder
        if obj.owner == request.user:
            return True
        
        # ✅ 2. Les administrateurs peuvent accéder
        if request.user.is_staff:
            return True
        
        # ✅ 3. Les organisations peuvent accéder
        from apps.organizations.models import OrganizationMember
        from apps.applications.models import ApplicationDocument
        from apps.applications.models import Application
        from apps.opportunities.models import Opportunity
        
        # Vérifier si le document est lié à une candidature
        app_docs = ApplicationDocument.objects.filter(document=obj)
        
        if app_docs.exists():
            app_ids = app_docs.values_list('application_id', flat=True)
            opp_ids = Application.objects.filter(id__in=app_ids).values_list('opportunity_id', flat=True)
            org_ids = Opportunity.objects.filter(id__in=opp_ids).values_list('organization_id', flat=True)
            
            has_access = OrganizationMember.objects.filter(
                user=request.user,
                organization_id__in=org_ids
            ).exists()
            
            if has_access:
                return True
        
        return False