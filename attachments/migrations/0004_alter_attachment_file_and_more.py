# Generated by Django 5.1.6 on 2025-02-23 10:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0003_attachment_service_request_alter_attachment_file'),
        ('service_requests', '0004_servicerequest_service_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(upload_to='attachments/uploads/'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='service_request',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='service_requests.servicerequest'),
            preserve_default=False,
        ),
    ]
