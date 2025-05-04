from django.urls import path
from .views import (
    upload_images, create_pavilion_with_images,
    get_districts, get_regions,
    predict_images, PavilionCardListCreateAPIView, ImageUploadRetrieveUpdateDestroyAPIView,
    PavilionCardRetrieveUpdateAPIView  # не забудь импортировать!
)

urlpatterns = [
    path('upload/', upload_images),
    path('districts/', get_districts),
    path('regions/', get_regions),
    path('pavilion/', create_pavilion_with_images),
    path('predict/', predict_images),  # ✅ корректный путь для Vue
    path('pavilions/', PavilionCardListCreateAPIView.as_view(), name='pavilion-list'),
    path('images/<int:pk>/', ImageUploadRetrieveUpdateDestroyAPIView.as_view(), name='image-detail'),
    path('pavilions/<int:pk>/', PavilionCardRetrieveUpdateAPIView.as_view()),

]
