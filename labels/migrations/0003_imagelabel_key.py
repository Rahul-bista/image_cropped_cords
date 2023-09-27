# Generated by Django 4.2.5 on 2023-09-27 13:11

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('labels', '0002_remove_imagelabel_image_height_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagelabel',
            name='key',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
