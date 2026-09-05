# apps/profiles/serializers.py
# C:\optimumjobs-backend\apps\profiles\serializers.py

from rest_framework import serializers
from apps.core.models import Skill
from apps.documents.models import Document  # ✅ Ajouté
from .models import CandidateProfile, Experience, Education, Language


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            'id', 'title', 'company', 'location',
            'start_date', 'end_date', 'is_current', 'description',
        ]

    def validate(self, attrs):
        if attrs.get('is_current') and attrs.get('end_date'):
            raise serializers.ValidationError(
                "Une expérience en cours ne doit pas avoir de date de fin."
            )
        return attrs


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'degree', 'institution', 'field_of_study',
            'start_date', 'end_date', 'is_current',
        ]

    def validate(self, attrs):
        if attrs.get('is_current') and attrs.get('end_date'):
            raise serializers.ValidationError(
                "Une formation en cours ne doit pas avoir de date de fin."
            )
        return attrs


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'level']


# ✅ NOUVEAU : Sérializer pour les documents
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'original_filename', 'document_type', 
            'file_size', 'mime_type', 'uploaded_at'
        ]


class CandidateProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source='skills', many=True, write_only=True, required=False,
    )
    experiences = ExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)

    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'first_name', 'last_name', 'phone', 'city', 'country', 'bio',
            'skills', 'skill_ids', 'experiences', 'education', 'languages',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ✅ MODIFIÉ : Ajout des documents dans le profil public
class PublicProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    documents = DocumentSerializer(source='user.documents', many=True, read_only=True)  # ✅ AJOUTÉ

    class Meta:
        model = CandidateProfile
        fields = [
            'id',
            'user_id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'city',
            'country',
            'bio',
            'skills',
            'experiences',
            'education',
            'languages',
            'documents',  # ✅ AJOUTÉ
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']