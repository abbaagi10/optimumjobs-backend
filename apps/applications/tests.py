from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.test import APITestCase

from apps.profiles.models import CandidateProfile
from apps.organizations.models import Organization, OrganizationMember
from apps.opportunities.models import Opportunity
from .models import Application

User = get_user_model()


class ApplicationCreationTests(APITestCase):
    """Tests de création de candidature et protection anti-doublon."""

    def setUp(self):
        self.candidate_user = User.objects.create_user(
            email='candidat@test.com', password='MotDePasseSolide123', role='candidate',
        )
        self.candidate_profile = CandidateProfile.objects.create(user=self.candidate_user)

        org_user = User.objects.create_user(
            email='org@test.com', password='MotDePasseSolide123', role='organization',
        )
        organization = Organization.objects.create(name='TechCorp')
        OrganizationMember.objects.create(
            organization=organization, user=org_user, role=OrganizationMember.Role.OWNER,
        )

        self.opportunity = Opportunity.objects.create(
            organization=organization, title='Développeur Backend', description='Poste Django',
            opportunity_type='job', status=Opportunity.Status.PUBLISHED,
        )

        self.client.force_authenticate(user=self.candidate_user)

    def test_candidate_can_apply_to_published_opportunity(self):
        """Un candidat peut postuler à une opportunité publiée."""
        response = self.client.post(f'/api/v1/opportunities/{self.opportunity.id}/apply/', {
            'cover_note': 'Je suis motivée',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'submitted')

    def test_cannot_apply_to_draft_opportunity(self):
        """Un candidat ne peut pas postuler à une opportunité non publiée."""
        self.opportunity.status = Opportunity.Status.DRAFT
        self.opportunity.save()

        response = self.client.post(f'/api/v1/opportunities/{self.opportunity.id}/apply/', {
            'cover_note': 'Je suis motivée',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_apply_twice_via_api(self):
        """
        TEST CRITIQUE : une deuxième candidature à la même opportunité
        est rejetée proprement via l'API (400, pas 500).
        """
        self.client.post(f'/api/v1/opportunities/{self.opportunity.id}/apply/', {'cover_note': 'Premier essai'})

        response = self.client.post(f'/api/v1/opportunities/{self.opportunity.id}/apply/', {'cover_note': 'Deuxième essai'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Application.objects.count(), 1)

    def test_database_constraint_prevents_duplicate_at_orm_level(self):
        """
        TEST CRITIQUE : la UniqueConstraint bloque un doublon même en contournant
        complètement l'API/le serializer — preuve que la protection est au niveau
        base de données, pas seulement applicative (voir Étape 8, section 2).
        """
        Application.objects.create(candidate=self.candidate_profile, opportunity=self.opportunity)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Application.objects.create(candidate=self.candidate_profile, opportunity=self.opportunity)

        # Une seule candidature doit exister malgré la tentative de doublon
        self.assertEqual(Application.objects.count(), 1)


class ApplicationPermissionTests(APITestCase):
    """Tests de permissions sur les candidatures."""

    def setUp(self):
        self.candidate_a = User.objects.create_user(
            email='candidatA@test.com', password='MotDePasseSolide123', role='candidate',
        )
        self.candidate_b = User.objects.create_user(
            email='candidatB@test.com', password='MotDePasseSolide123', role='candidate',
        )
        self.profile_a = CandidateProfile.objects.create(user=self.candidate_a)

        self.org_user = User.objects.create_user(
            email='org@test.com', password='MotDePasseSolide123', role='organization',
        )
        self.organization = Organization.objects.create(name='TechCorp')
        OrganizationMember.objects.create(
            organization=self.organization, user=self.org_user, role=OrganizationMember.Role.OWNER,
        )

        self.opportunity = Opportunity.objects.create(
            organization=self.organization, title='Développeur Backend', description='Poste Django',
            opportunity_type='job', status=Opportunity.Status.PUBLISHED,
        )
        self.application = Application.objects.create(candidate=self.profile_a, opportunity=self.opportunity)

    def test_candidate_b_cannot_view_candidate_a_application(self):
        """TEST CRITIQUE : un candidat ne peut pas consulter la candidature d'un autre."""
        self.client.force_authenticate(user=self.candidate_b)

        response = self.client.get(f'/api/v1/applications/{self.application.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organization_can_view_application_to_its_opportunity(self):
        """Une organisation peut consulter une candidature reçue sur sa propre offre."""
        self.client.force_authenticate(user=self.org_user)

        response = self.client.get(f'/api/v1/applications/{self.application.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_organization_can_update_application_status(self):
        """Une organisation peut faire progresser le statut d'une candidature reçue."""
        self.client.force_authenticate(user=self.org_user)

        response = self.client.patch(f'/api/v1/applications/{self.application.id}/status/', {
            'status': 'shortlisted',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'shortlisted')

    def test_organization_cannot_set_status_to_withdrawn(self):
        """Seul le candidat peut retirer sa propre candidature, pas l'organisation."""
        self.client.force_authenticate(user=self.org_user)

        response = self.client.patch(f'/api/v1/applications/{self.application.id}/status/', {
            'status': 'withdrawn',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_candidate_can_withdraw_own_application(self):
        """Le candidat propriétaire peut retirer sa candidature."""
        self.client.force_authenticate(user=self.candidate_a)

        response = self.client.post(f'/api/v1/applications/{self.application.id}/withdraw/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'withdrawn')

    def test_unrelated_organization_cannot_view_application(self):
        """Une organisation sans lien avec l'opportunité ne peut pas voir la candidature."""
        other_org_user = User.objects.create_user(
            email='autre_org@test.com', password='MotDePasseSolide123', role='organization',
        )
        other_organization = Organization.objects.create(name='AutreOrg')
        OrganizationMember.objects.create(
            organization=other_organization, user=other_org_user, role=OrganizationMember.Role.OWNER,
        )

        self.client.force_authenticate(user=other_org_user)
        response = self.client.get(f'/api/v1/applications/{self.application.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)