from rest_framework import serializers

from apps.core.models import Skill
from apps.organizations.models import Organization
from .models import Opportunity, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class OpportunityPublicSerializer(serializers.ModelSerializer):
    """
    Vue allégée pour les visiteurs/candidats : pas de champs de workflow interne
    (rejection_reason, status en détail...), uniquement l'essentiel pour consulter.
    """
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    category = CategorySerializer(read_only=True)
    skills = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id', 'title', 'description', 'opportunity_type',
            'organization_name', 'category', 'skills',
            'city', 'country', 'is_remote',
            'experience_level', 'education_level', 'contract_type',
            'salary_min', 'salary_max', 'duration_weeks',
            'application_deadline', 'published_at',
        ]


class OpportunityManageSerializer(serializers.ModelSerializer):
    """
    Vue complète pour l'organisation qui gère ses propres opportunités
    (création, modification, suivi du statut).
    """
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source='skills', many=True, write_only=True, required=False,
    )
    skills = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id', 'organization', 'category', 'title', 'description', 'opportunity_type',
            'skills', 'skill_ids',
            'city', 'country', 'is_remote',
            'experience_level', 'education_level', 'contract_type',
            'salary_min', 'salary_max', 'duration_weeks',
            'status', 'rejection_reason',
            'application_deadline', 'published_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'organization', 'status', 'rejection_reason', 'published_at',
            'created_at', 'updated_at',
        ]