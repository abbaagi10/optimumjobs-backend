from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Organization, OrganizationMember

User = get_user_model()


class OrganizationMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = OrganizationMember
        fields = ['id', 'user', 'email', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']
        extra_kwargs = {'user': {'write_only': True}}


class OrganizationSerializer(serializers.ModelSerializer):
    members = OrganizationMemberSerializer(many=True, read_only=True)
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'description', 'website', 'city', 'country',
            'is_verified', 'members', 'my_role', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']

    def get_my_role(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        membership = obj.members.filter(user=request.user).first()
        return membership.role if membership else None