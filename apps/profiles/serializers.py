from rest_framework import serializers

from apps.core.models import Skill
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