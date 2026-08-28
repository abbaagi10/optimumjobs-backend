from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CandidateProfile, Experience

User = get_user_model()


class MyProfileTests(APITestCase):
    """Tests pour la consultation et modification de son propre profil."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='candidat@test.com', password='MotDePasseSolide123', role='candidate',
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile_creates_it_automatically(self):
        """Le premier accès à /profile/ crée automatiquement le profil (get_or_create)."""
        self.assertEqual(CandidateProfile.objects.count(), 0)

        response = self.client.get('/api/v1/profile/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CandidateProfile.objects.count(), 1)

    def test_update_profile_success(self):
        """Un candidat peut modifier son propre profil."""
        response = self.client.patch('/api/v1/profile/', {
            'first_name': 'Amina',
            'city': 'Niamey',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Amina')
        self.assertEqual(response.data['city'], 'Niamey')

    def test_cannot_update_readonly_fields(self):
        """Les champs read_only (id, created_at...) ne peuvent pas être modifiés par le client."""
        response = self.client.get('/api/v1/profile/')
        original_id = response.data['id']

        response = self.client.patch('/api/v1/profile/', {'id': 999})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], original_id)


class ExperienceOwnershipTests(APITestCase):
    """
    Tests critiques : un candidat ne doit jamais pouvoir accéder
    ou modifier les données d'un autre candidat (Étape 3 + Étape 4).
    """

    def setUp(self):
        self.candidate_a = User.objects.create_user(
            email='candidatA@test.com', password='MotDePasseSolide123', role='candidate',
        )
        self.candidate_b = User.objects.create_user(
            email='candidatB@test.com', password='MotDePasseSolide123', role='candidate',
        )

        self.profile_a = CandidateProfile.objects.create(user=self.candidate_a)

        self.experience_a = Experience.objects.create(
            profile=self.profile_a,
            title='Développeuse',
            company='TechCorp',
            start_date='2023-01-01',
            is_current=True,
        )

    def test_candidate_can_create_own_experience(self):
        """Un candidat peut ajouter une expérience à son propre profil."""
        self.client.force_authenticate(user=self.candidate_a)

        response = self.client.post('/api/v1/profile/experiences/', {
            'title': 'Stagiaire',
            'company': 'StartupXYZ',
            'start_date': '2022-01-01',
            'end_date': '2022-06-01',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_candidate_b_cannot_view_candidate_a_experience(self):
        """
        TEST CRITIQUE : un candidat ne peut pas consulter une expérience
        appartenant à un autre candidat (has_object_permission).
        """
        self.client.force_authenticate(user=self.candidate_b)

        response = self.client.get(f'/api/v1/profile/experiences/{self.experience_a.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_candidate_b_cannot_delete_candidate_a_experience(self):
        """TEST CRITIQUE : un candidat ne peut pas supprimer l'expérience d'un autre."""
        self.client.force_authenticate(user=self.candidate_b)

        response = self.client.delete(f'/api/v1/profile/experiences/{self.experience_a.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # L'expérience doit toujours exister en base
        self.assertTrue(Experience.objects.filter(id=self.experience_a.id).exists())

    def test_candidate_b_experience_list_does_not_include_candidate_a(self):
        """
        TEST CRITIQUE : la liste des expériences d'un candidat ne doit jamais
        inclure celles d'un autre (get_queryset filtré).
        """
        self.client.force_authenticate(user=self.candidate_b)

        response = self.client.get('/api/v1/profile/experiences/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_unauthenticated_user_cannot_access_experiences(self):
        """Sans authentification, l'accès est refusé (401, pas 403)."""
        response = self.client.get('/api/v1/profile/experiences/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)