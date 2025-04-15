from django.urls import path
from .views import upload_images

urlpatterns = [
    path('upload/', upload_images, name='upload-images'),  # → /api/upload/
]
