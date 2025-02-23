from rest_framework import serializers
from .models import ServiceRequest
from attachments.models import Attachment
import random
from django.contrib.auth import get_user_model

User = get_user_model()


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for handling file uploads within service requests."""

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']


class ServiceRequestSerializer(serializers.ModelSerializer):
    """Serializer for ServiceRequest model with attachment handling."""

    attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,  # Accept file uploads but don't return them in response
        required=False
    )

    uploaded_attachments = AttachmentSerializer(many=True, read_only=True, source="attachments")

    class Meta:
        model = ServiceRequest
        fields = ['id', 'customer', 'support_staff', 'title', 'description', 'status',
                  'attachments', 'uploaded_attachments', 'created_at', 'updated_at']
        read_only_fields = ('customer', 'support_staff', 'status', 'created_at', 'updated_at')

    def validate_title(self, value):
        """Ensure title is not too short."""
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value

    def validate_description(self, value):
        """Ensure description has enough detail."""
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value

    def create(self, validated_data):
        """Override create to handle file uploads and associate them with the request."""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required to assign customer.")

        files = validated_data.pop('attachments', [])
        validated_data["customer"] = request.user

        # Assign a random support staff if available
        support_staff = User.objects.filter(role="support_staff")
        validated_data["support_staff"] = random.choice(support_staff) if support_staff.exists() else None

        # Create the service request
        service_request = ServiceRequest.objects.create(**validated_data)

        # Save attachments
        for file in files:
            Attachment.objects.create(file=file, service_request=service_request)

        return service_request
