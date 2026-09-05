# apps/administration/urls.py
from django.urls import path

from .views import (
    AdminUserListView,
    AdminToggleUserActiveView,
    AdminOrganizationListView,
    AdminVerifyOrganizationView,
    AdminPendingOpportunityListView,
    AdminDashboardStatsView,
    
)

urlpatterns = [
    # Dashboard
    path('admin/dashboard/', AdminDashboardStatsView.as_view(), name='admin-dashboard'),

    # Utilisateurs
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/toggle-active/', AdminToggleUserActiveView.as_view(), name='admin-user-toggle-active'),

    # Organisations
    path('admin/organizations/', AdminOrganizationListView.as_view(), name='admin-organization-list'),
    path('admin/organizations/<int:pk>/verify/', AdminVerifyOrganizationView.as_view(), name='admin-organization-verify'),

    # Opportunités
    path('admin/opportunities/pending/', AdminPendingOpportunityListView.as_view(), name='admin-opportunity-pending'),
    
    
]