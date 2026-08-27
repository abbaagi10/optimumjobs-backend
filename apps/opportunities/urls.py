from django.urls import path

from .views import (
    PublicOpportunityListView, PublicOpportunityDetailView,
    MyOrganizationOpportunityListCreateView, MyOrganizationOpportunityDetailView,
    SubmitForReviewView, ReviewOpportunityView, PublishOpportunityView, CloseOpportunityView,
)

urlpatterns = [
    # Public
    path('opportunities/', PublicOpportunityListView.as_view(), name='opportunity-public-list'),
    path('opportunities/<int:pk>/', PublicOpportunityDetailView.as_view(), name='opportunity-public-detail'),

    # Gestion côté organisation
    path('organizations/<int:org_id>/opportunities/', MyOrganizationOpportunityListCreateView.as_view(), name='opportunity-org-list'),
    path('opportunities/manage/<int:pk>/', MyOrganizationOpportunityDetailView.as_view(), name='opportunity-manage-detail'),

    # Transitions de workflow
    path('opportunities/manage/<int:pk>/submit/', SubmitForReviewView.as_view(), name='opportunity-submit'),
    path('opportunities/manage/<int:pk>/review/', ReviewOpportunityView.as_view(), name='opportunity-review'),
    path('opportunities/manage/<int:pk>/publish/', PublishOpportunityView.as_view(), name='opportunity-publish'),
    path('opportunities/manage/<int:pk>/close/', CloseOpportunityView.as_view(), name='opportunity-close'),
]