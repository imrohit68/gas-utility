import random
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from attachments.models import Attachment


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    SERVICE_TYPES = [
        ("installation", "Installation"),
        ("maintenance", "Maintenance"),
        ("repair", "Repair"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requests"
    )
    support_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_requests"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default="maintenance")

    def assign_support_staff(self):
        User = get_user_model()  # Avoid direct import
        support_staff_users = User.objects.filter(role="support_staff")
        if support_staff_users.exists():
            self.support_staff = random.choice(support_staff_users)

    def save(self, *args, **kwargs):
        if self.support_staff is None:
            self.assign_support_staff()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Request {self.id} - {self.status}"
