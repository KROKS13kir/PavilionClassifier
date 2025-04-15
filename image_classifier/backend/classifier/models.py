# image_classifier/models.py
from django.db import models

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='uploads/')
    predicted_class = models.CharField(max_length=50, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.predicted_class} ({self.confidence:.2f})"
