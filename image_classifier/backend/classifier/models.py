# image_classifier/models.py
from django.db import models

from django.db import models

from classifier.utils import delete_from_s3


# classifier/models.py
class District(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short = models.CharField(max_length=20, unique=True)




class Region(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='regions')

    class Meta:
        unique_together = ('name', 'district')  # ✅ Уникальность пары (name, district)
        verbose_name = "Район"
        verbose_name_plural = "Районы"

    def __str__(self):
        return f"{self.district.name} — {self.name}"


class PavilionCard(models.Model):
    mpv_code = models.CharField(max_length=100)
    stop_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    pavilion_number = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=[("A", "A"), ("B", "B"), ("C", "C")])
    pavilion_class = models.CharField(max_length=100)
    balance_holder = models.CharField(max_length=100, choices=[("Город", "Город"), ("Частная", "Частная")])
    address = models.TextField(blank=True)
    confirmed_state = models.CharField(max_length=100, blank=True)


class ImageUpload(models.Model):
    image_url = models.CharField(max_length=500)  # теперь просто ссылка, а не ImageField
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    predicted_class = models.CharField(max_length=100, blank=True, null=True)
    confidence = models.FloatField(null=True, blank=True)
    confirmed_state = models.CharField(max_length=100, blank=True)
    pavilion = models.ForeignKey('PavilionCard', on_delete=models.CASCADE, related_name='images', null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.image_url:
            try:
                delete_from_s3(self.image_url)
            except Exception as e:
                print(f"⚠️ Ошибка при удалении из S3: {e}")
        super().delete(*args, **kwargs)








