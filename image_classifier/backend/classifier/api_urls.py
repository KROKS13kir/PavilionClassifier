from django.urls import path
from .views import (
    upload_images, create_pavilion_with_images,
    get_districts, get_regions,
    predict_images  # не забудь импортировать!
)

urlpatterns = [
    path('upload/', upload_images),
    path('districts/', get_districts),
    path('regions/', get_regions),
    path('pavilion/', create_pavilion_with_images),
    path('predict/', predict_images),  # ✅ корректный путь для Vue
]
