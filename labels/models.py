import uuid

from django.db import models


# Create your models here.


class ImageLabel(models.Model):
    key = models.UUIDField(default=uuid.uuid4)
    original_image = models.ImageField(max_length=600, upload_to='uploads/')
    mask_image = models.ImageField(max_length=600, upload_to='uploads/')
    transparent_image = models.ImageField(max_length=600, upload_to='uploads/')

    def __str__(self):
        return self.original_image.name
