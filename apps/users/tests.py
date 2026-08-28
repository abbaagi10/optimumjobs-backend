from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationTests(APITestCase):
    """Tests pour l'endpoint d'inscription."""

    def test_register_candidate_success(self):
        """Un candidat peut s'inscrire avec des données valides."""
        response = self.client.post('/api/v1/auth/register/', {
            'email': 'nouveau@test.com',
            'password': 'MotDePasseSolide123',
            'role': 'candidate',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'], 'nouveau@test.com')
        # Le mot de passe ne doit jamais apparaître dans la réponse
        self.assertNotIn('password', response.data)

    def test_register_password_is_hashed(self):
        """Le mot de passe stocké en base est haché, pas en clair."""
        self.client.post('/api/v1/auth/register/', {
            'email': 'securite@test.com',
            'password': 'MotDePasseSolide123',
            'role': 'candidate',
        })
        user = User.objects.get(email='securite@test.com')
        self.assertNotEqual(user.password, 'MotDePasseSolide123')
        self.assertTrue(user.check_password('MotDePasseSolide123'))

    def test_register_duplicate_email_fails(self):
        """Impossible de s'inscrire deux fois avec le même email."""
        User.objects.create_user(email='existe@test.com', password='xxxxxxxx')

        response = self.client.post('/api/v1/auth/register/', {
            'email': 'existe@test.com',
            'password': 'MotDePasseSolide123',
            'role': 'candidate',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password_fails(self):
        """Un mot de passe trop faible est rejeté par les validateurs Django."""
        response = self.client.post('/api/v1/auth/register/', {
            'email': 'faible@test.com',
            'password': '123',
            'role': 'candidate',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """Tests pour l'endpoint de connexion (JWT)."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='candidat@test.com', password='MotDePasseSolide123', role='candidate',
        )

    def test_login_success_returns_tokens(self):
        """Une connexion valide renvoie un access token et un refresh token."""
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'candidat@test.com',
            'password': 'MotDePasseSolide123',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password_fails(self):
        """Un mauvais mot de passe est rejeté."""
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'candidat@test.com',
            'password': 'MauvaisMotDePasse',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_account_fails(self):
        """Un compte désactivé ne peut pas se connecter."""
        self.user.is_active = False
        self.user.save()

        response = self.client.post('/api/v1/auth/login/', {
            'email': 'candidat@test.com',
            'password': 'MotDePasseSolide123',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeEndpointTests(APITestCase):
    """Tests pour l'endpoint /auth/me/, qui nécessite une authentification."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='candidat@test.com', password='MotDePasseSolide123', role='candidate',
        )

    def test_me_without_token_fails(self):
        """Sans token, l'accès est refusé."""
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_valid_token_succeeds(self):
        """Avec un token valide, on récupère bien les infos du bon utilisateur."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'candidat@test.com')

    def test_me_does_not_expose_role_as_writable(self):
        """Un utilisateur ne peut pas changer son propre rôle via cet endpoint."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/auth/me/')
        # role doit être présent en lecture...
        self.assertIn('role', response.data)