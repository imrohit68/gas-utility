from rest_framework import serializers
from .models import ServiceRequest
from attachments.models import Attachment
import random
from django.contrib.auth import get_user_model

User = get_user_model()


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']


class ServiceRequestSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    uploaded_attachments = AttachmentSerializer(many=True, read_only=True, source="attachments")

    class Meta:
        model = ServiceRequest
        fields = ['id', 'customer', 'support_staff', 'title', 'service_type','description', 'status',
                  'attachments', 'uploaded_attachments', 'created_at', 'updated_at']
        read_only_fields = ('customer', 'support_staff', 'status', 'created_at', 'updated_at')

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value

    def validate_description(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required to assign customer.")

        files = validated_data.pop('attachments', [])
        validated_data["customer"] = request.user

        support_staff = User.objects.filter(role="support_staff")
        validated_data["support_staff"] = random.choice(support_staff) if support_staff.exists() else None

        service_request = ServiceRequest.objects.create(**validated_data)

        for file in files:
            Attachment.objects.create(file=file, service_request=service_request)

        return service_request
