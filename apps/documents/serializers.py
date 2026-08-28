from rest_framework import serializers

from .models import Document
from .validators import validate_file_size, validate_file_extension, validate_file_mime_type


class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        write_only=True,
        validators=[validate_file_size, validate_file_extension, validate_file_mime_type],
    )

    class Meta:
        model = Document
        fields = [
            'id', 'document_type', 'file', 'original_filename',
            'file_size', 'mime_type', 'uploaded_at',
        ]
        read_only_fields = ['id', 'original_filename', 'file_size', 'mime_type', 'uploaded_at']

    def create(self, validated_data):
        file = validated_data['file']
        validated_data['original_filename'] = file.name
        validated_data['file_size'] = file.size
        validated_data['mime_type'] = file.content_type
        return super().create(validated_data)