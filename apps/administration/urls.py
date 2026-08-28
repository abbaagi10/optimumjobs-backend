from django.urls import path

from .views import (
    AdminUserListView, AdminToggleUserActiveView,
    AdminOrganizationListView, AdminVerifyOrganizationView,
    AdminPendingOpportunityListView, AdminDashboardStatsView,
)

urlpatterns = [
    path('admin/dashboard/', AdminDashboardStatsView.as_view(), name='admin-dashboard'),

    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/toggle-active/', AdminToggleUserActiveView.as_view(), name='admin-user-toggle-active'),

    path('admin/organizations/', AdminOrganizationListView.as_view(), name='admin-organization-list'),
    path('admin/organizations/<int:pk>/verify/', AdminVerifyOrganizationView.as_view(), name='admin-organization-verify'),

    path('admin/opportunities/pending/', AdminPendingOpportunityListView.as_view(), name='admin-opportunity-pending'),
]