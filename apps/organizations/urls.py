from django.urls import path

from .views import (
    OrganizationListCreateView, OrganizationDetailView,
    OrganizationMemberListCreateView,
)

urlpatterns = [
    path('organizations/', OrganizationListCreateView.as_view(), name='organization-list'),
    path('organizations/<int:pk>/', OrganizationDetailView.as_view(), name='organization-detail'),
    path('organizations/<int:org_id>/members/', OrganizationMemberListCreateView.as_view(), name='organization-member-list'),
]