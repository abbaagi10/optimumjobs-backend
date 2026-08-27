from rest_framework import generics, permissions

from apps.core.permissions import IsCandidate
from .models import CandidateProfile, Experience, Education, Language
from .permissions import IsProfileOwner
from .serializers import (
    CandidateProfileSerializer, ExperienceSerializer,
    EducationSerializer, LanguageSerializer,
)


class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/profile/   -> voir mon propre profil
    PATCH /api/v1/profile/   -> modifier mon propre profil
    """
    serializer_class = CandidateProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def get_object(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return profile


class ExperienceListCreateView(generics.ListCreateAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Experience.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)


class ExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate, IsProfileOwner]
    queryset = Experience.objects.all()


class EducationListCreateView(generics.ListCreateAPIView):
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Education.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)


class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate, IsProfileOwner]
    queryset = Education.objects.all()


class LanguageListCreateView(generics.ListCreateAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Language.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)


class LanguageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate, IsProfileOwner]
    queryset = Language.objects.all()