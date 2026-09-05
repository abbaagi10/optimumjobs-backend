# apps/profiles/views.py
# C:\optimumjobs-backend\apps\profiles\views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from apps.users.serializers import UserSerializer
from .models import CandidateProfile, Experience, Education, Language
from .serializers import (
    CandidateProfileSerializer,
    PublicProfileSerializer,  # ✅ AJOUTÉ
    ExperienceSerializer, 
    EducationSerializer, 
    LanguageSerializer
)

User = get_user_model()


# ============================================================
# PERMISSIONS PERSONNALISÉES
# ============================================================

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission qui permet à l'utilisateur de modifier ses propres données
    ou à un administrateur de tout modifier.
    """
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.is_staff:
            return True
        
        # Vérifier si l'objet a un champ 'profile' avec un 'user'
        if hasattr(obj, 'profile') and hasattr(obj.profile, 'user'):
            return obj.profile.user == request.user
        
        # Vérifier si l'objet a un champ 'user' directement
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


# ============================================================
# PROFIL UTILISATEUR (propre profil)
# ============================================================

class MyProfileView(APIView):
    """
    GET /api/v1/profile/
    Récupère le profil de l'utilisateur connecté.
    
    PATCH /api/v1/profile/
    Met à jour partiellement le profil de l'utilisateur connecté.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Récupère le profil de l'utilisateur connecté avec toutes ses relations"""
        try:
            user = request.user
            
            # Récupérer ou créer le profil
            profile, created = CandidateProfile.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                }
            )
            
            # Récupérer les relations via le profil
            experiences = Experience.objects.filter(profile=profile).order_by('-start_date')
            education = Education.objects.filter(profile=profile).order_by('-start_date')
            languages = Language.objects.filter(profile=profile).order_by('name')
            
            # Construire la réponse
            profile_data = {
                'id': profile.id,
                'first_name': profile.first_name or user.first_name or '',
                'last_name': profile.last_name or user.last_name or '',
                'phone': profile.phone or '',
                'city': profile.city or '',
                'country': profile.country or '',
                'bio': profile.bio or '',
                'experiences': ExperienceSerializer(experiences, many=True).data,
                'education': EducationSerializer(education, many=True).data,
                'languages': LanguageSerializer(languages, many=True).data,
            }
            
            return Response(profile_data)
            
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request):
        """Met à jour partiellement le profil de l'utilisateur connecté"""
        try:
            allowed_fields = ['first_name', 'last_name', 'phone', 'city', 'country', 'bio']
            filtered_data = {k: v for k, v in request.data.items() if k in allowed_fields}

            if not filtered_data:
                return Response(
                    {"detail": "Aucun champ valide à mettre à jour."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Récupérer ou créer le profil
            profile, created = CandidateProfile.objects.get_or_create(
                user=request.user
            )
            
            # Mettre à jour les champs du profil
            for field, value in filtered_data.items():
                setattr(profile, field, value)
            profile.save()

            # Mettre à jour l'utilisateur si besoin
            if 'first_name' in filtered_data:
                request.user.first_name = filtered_data['first_name']
            if 'last_name' in filtered_data:
                request.user.last_name = filtered_data['last_name']
            request.user.save()

            # Retourner les données mises à jour
            return Response({
                'id': profile.id,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'phone': profile.phone,
                'city': profile.city,
                'country': profile.country,
                'bio': profile.bio,
            })

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================
# ✅ PROFIL PUBLIC - CORRIGÉ
# ============================================================

class PublicProfileView(generics.RetrieveAPIView):
    """
    GET /api/v1/profile/<int:pk>/
    Vue publique pour voir le profil d'un candidat.
    Accessible par les organisations et les administrateurs.
    """
    # ✅ UTILISER PublicProfileSerializer au lieu de CandidateProfileSerializer
    serializer_class = PublicProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CandidateProfile.objects.all()


# ============================================================
# EXPÉRIENCES PROFESSIONNELLES
# ============================================================

class ExperienceListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/profile/experiences/ - Liste les expériences
    POST /api/v1/profile/experiences/ - Crée une expérience
    """
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retourne uniquement les expériences du profil de l'utilisateur connecté"""
        try:
            profile = CandidateProfile.objects.get(user=self.request.user)
            return Experience.objects.filter(profile=profile).order_by('-start_date')
        except CandidateProfile.DoesNotExist:
            return Experience.objects.none()

    def perform_create(self, serializer):
        """Associe automatiquement l'expérience au profil de l'utilisateur connecté"""
        profile, created = CandidateProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(profile=profile)


class ExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/v1/profile/experiences/<int:pk>/ - Détail d'une expérience
    PATCH /api/v1/profile/experiences/<int:pk>/ - Modifie une expérience
    DELETE /api/v1/profile/experiences/<int:pk>/ - Supprime une expérience
    """
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """Retourne uniquement les expériences du profil de l'utilisateur connecté"""
        try:
            profile = CandidateProfile.objects.get(user=self.request.user)
            return Experience.objects.filter(profile=profile)
        except CandidateProfile.DoesNotExist:
            return Experience.objects.none()


# ============================================================
# FORMATIONS / ÉDUCATIONS
# ============================================================

class EducationListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/profile/education/ - Liste les formations
    POST /api/v1/profile/education/ - Crée une formation
    """
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retourne uniquement les formations du profil de l'utilisateur connecté"""
        try:
            profile = CandidateProfile.objects.get(user=self.request.user)
            return Education.objects.filter(profile=profile).order_by('-start_date')
        except CandidateProfile.DoesNotExist:
            return Education.objects.none()

    def perform_create(self, serializer):
        """Associe automatiquement la formation au profil de l'utilisateur connecté"""
        profile, created = CandidateProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(profile=profile)


class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/v1/profile/education/<int:pk>/ - Détail d'une formation
    PATCH /api/v1/profile/education/<int:pk>/ - Modifie une formation
    DELETE /api/v1/profile/education/<int:pk>/ - Supprime une formation
    """
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """Retourne uniquement les formations du profil de l'utilisateur connecté"""
        try:
            profile = CandidateProfile.objects.get(user=self.request.user)
            return Education.objects.filter(profile=profile)
        except CandidateProfile.DoesNotExist:
            return Education.objects.none()


# ============================================================
# LANGUES
# ============================================================

class LanguageListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/profile/languages/ - Liste les langues
    POST /api/v1/profile/languages/ - Crée une langue
    """
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retourne uniquement les langues du profil de l'utilisateur connecté"""
        try:
            profile = CandidateProfile.objects.get(user=self.request.user)
            return Language.objects.filter(profile=profile).order_by('name')
        except CandidateProfile.DoesNotExist:
            return Language.objects.none()

    def perform_create(self, serializer):
        """Associe automatiquement la langue au profil de l'utilisateur connecté"""
        profile, created = CandidateProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(profile=profile)


class LanguageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/v1/profile/languages/<int:pk>/ - Détail d'une langue
    PATCH /api/v1/profile/languages/<int:pk>/ - Modifie une langue
    DELETE /api/v1/profile/languages/<int:pk>/ - Supprime une langue
    """
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """Retourne uniquement les langues du profil de l'utilisateur connecté"""
        try:
            profile = CandidateProfile.objects.get(user=self.request.user)
            return Language.objects.filter(profile=profile)
        except CandidateProfile.DoesNotExist:
            return Language.objects.none()