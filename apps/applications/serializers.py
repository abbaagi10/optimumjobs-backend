from rest_framework import serializers

from apps.opportunities.models import Opportunity
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    opportunity_title = serializers.CharField(source='opportunity.title', read_only=True)
    candidate_email = serializers.CharField(source='candidate.user.email', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'candidate', 'opportunity', 'opportunity_title', 'candidate_email',
            'status', 'cover_note', 'submitted_at', 'updated_at',
        ]
        read_only_fields = ['id', 'candidate', 'status', 'submitted_at', 'updated_at']


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['cover_note']

    def validate(self, attrs):
        opportunity = self.context['opportunity']
        if opportunity.status != Opportunity.Status.PUBLISHED:
            raise serializers.ValidationError(
                "Vous ne pouvez postuler qu'à une opportunité publiée."
            )
        return attrs


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']

    def validate_status(self, value):
        if value == Application.Status.WITHDRAWN:
            raise serializers.ValidationError(
                "Seul le candidat peut retirer sa candidature."
            )
        return value