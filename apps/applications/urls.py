from django.urls import path

from .views import (
    ApplyToOpportunityView, MyApplicationListView, ApplicationDetailView,
    OrganizationApplicationListView, UpdateApplicationStatusView, WithdrawApplicationView,
)

urlpatterns = [
    path('opportunities/<int:pk>/apply/', ApplyToOpportunityView.as_view(), name='opportunity-apply'),
    path('opportunities/<int:pk>/applications/', OrganizationApplicationListView.as_view(), name='opportunity-applications'),

    path('applications/', MyApplicationListView.as_view(), name='application-list'),
    path('applications/<int:pk>/', ApplicationDetailView.as_view(), name='application-detail'),
    path('applications/<int:pk>/status/', UpdateApplicationStatusView.as_view(), name='application-status'),
    path('applications/<int:pk>/withdraw/', WithdrawApplicationView.as_view(), name='application-withdraw'),
]