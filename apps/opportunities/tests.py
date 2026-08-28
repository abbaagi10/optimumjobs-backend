from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.organizations.models import Organization, OrganizationMember
from .models import Opportunity

User = get_user_model()


class OpportunityWorkflowTests(APITestCase):
    """
    Tests du cycle de vie complet d'une opportunité :
    DRAFT -> PENDING_REVIEW -> APPROVED -> PUBLISHED -> CLOSED
    """

    def setUp(self):
        self.org_user = User.objects.create_user(
            email='org@test.com', password='MotDePasseSolide123', role='organization',
        )
        self.admin_user = User.objects.create_user(
            email='admin@test.com', password='MotDePasseSolide123', role='admin', is_staff=True,
        )
        self.candidate_user = User.objects.create_user(
            email='candidat@test.com', password='MotDePasseSolide123', role='candidate',
        )

        self.organization = Organization.objects.create(name='TechCorp')
        OrganizationMember.objects.create(
            organization=self.organization, user=self.org_user, role=OrganizationMember.Role.OWNER,
        )

    def _create_opportunity(self):
        self.client.force_authenticate(user=self.org_user)
        response = self.client.post(f'/api/v1/organizations/{self.organization.id}/opportunities/', {
            'title': 'Développeur Backend',
            'description': 'Poste Django',
            'opportunity_type': 'job',
            'contract_type': 'cdi',
        })
        return response.data['id']

    def test_new_opportunity_starts_as_draft(self):
        """Une opportunité créée démarre toujours en statut DRAFT."""
        opp_id = self._create_opportunity()
        opportunity = Opportunity.objects.get(id=opp_id)
        self.assertEqual(opportunity.status, Opportunity.Status.DRAFT)

    def test_draft_opportunity_not_visible_publicly(self):
        """Une opportunité en DRAFT n'apparaît pas dans la liste publique."""
        self._create_opportunity()

        response = self.client.get('/api/v1/opportunities/')

        self.assertEqual(response.data['count'], 0)

    def test_full_workflow_to_published(self):
        """
        TEST CRITIQUE : parcourt tout le workflow et vérifie qu'une opportunité
        publiée devient visible publiquement, avec les bonnes permissions à chaque étape.
        """
        opp_id = self._create_opportunity()

        # Soumission par l'organisation
        self.client.force_authenticate(user=self.org_user)
        response = self.client.post(f'/api/v1/opportunities/manage/{opp_id}/submit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending_review')

        # Approbation par l'admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(f'/api/v1/opportunities/manage/{opp_id}/review/', {'action': 'approve'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')

        # Publication par l'organisation
        self.client.force_authenticate(user=self.org_user)
        response = self.client.post(f'/api/v1/opportunities/manage/{opp_id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'published')
        self.assertIsNotNone(response.data['published_at'])

        # Vérification : visible publiquement maintenant
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/opportunities/')
        self.assertEqual(response.data['count'], 1)

    def test_candidate_cannot_approve_opportunity(self):
        """TEST CRITIQUE : seul un admin peut approuver une opportunité."""
        opp_id = self._create_opportunity()

        self.client.force_authenticate(user=self.org_user)
        self.client.post(f'/api/v1/opportunities/manage/{opp_id}/submit/')

        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.post(f'/api/v1/opportunities/manage/{opp_id}/review/', {'action': 'approve'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_approve_opportunity_still_in_draft(self):
        """Une opportunité en DRAFT (pas encore soumise) ne peut pas être directement approuvée."""
        opp_id = self._create_opportunity()

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(f'/api/v1/opportunities/manage/{opp_id}/review/', {'action': 'approve'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_publish_unapproved_opportunity(self):
        """Une opportunité non approuvée ne peut pas être publiée directement."""
        opp_id = self._create_opportunity()

        self.client.force_authenticate(user=self.org_user)
        response = self.client.post(f'/api/v1/opportunities/manage/{opp_id}/publish/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_organization_cannot_modify_opportunity(self):
        """Une organisation ne peut pas gérer les opportunités d'une autre organisation."""
        opp_id = self._create_opportunity()

        other_org_user = User.objects.create_user(
            email='autre_org@test.com', password='MotDePasseSolide123', role='organization',
        )
        other_organization = Organization.objects.create(name='AutreOrg')
        OrganizationMember.objects.create(
            organization=other_organization, user=other_org_user, role=OrganizationMember.Role.OWNER,
        )

        self.client.force_authenticate(user=other_org_user)
        response = self.client.post(f'/api/v1/opportunities/manage/{opp_id}/submit/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OpportunitySearchTests(APITestCase):
    """Tests de recherche et filtrage (Étape 7)."""

    def setUp(self):
        self.org_user = User.objects.create_user(
            email='org@test.com', password='MotDePasseSolide123', role='organization',
        )
        organization = Organization.objects.create(name='TechCorp')
        OrganizationMember.objects.create(
            organization=organization, user=self.org_user, role=OrganizationMember.Role.OWNER,
        )

        self.published_job = Opportunity.objects.create(
            organization=organization, title='Développeur Django', description='Poste backend',
            opportunity_type='job', status=Opportunity.Status.PUBLISHED,
        )
        self.published_internship = Opportunity.objects.create(
            organization=organization, title='Stagiaire Marketing', description='Stage communication',
            opportunity_type='internship', status=Opportunity.Status.PUBLISHED,
        )

    def test_search_by_keyword(self):
        response = self.client.get('/api/v1/opportunities/?search=Django')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Développeur Django')

    def test_filter_by_type(self):
        response = self.client.get('/api/v1/opportunities/?type=internship')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Stagiaire Marketing')

    def test_filter_with_no_match_returns_empty(self):
        response = self.client.get('/api/v1/opportunities/?search=Comptabilite')
        self.assertEqual(response.data['count'], 0)