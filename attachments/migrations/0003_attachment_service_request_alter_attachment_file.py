# Generated by Django 5.1.6 on 2025-02-22 08:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0002_alter_attachment_file'),
        ('service_requests', '0003_remove_servicerequest_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='service_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='service_requests.servicerequest'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(upload_to='attachments/'),
        ),
    ]
