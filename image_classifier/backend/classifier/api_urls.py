from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    upload_images,
    create_pavilion_with_images,
    get_districts,
    get_regions,
    predict_images,
    PavilionCardListCreateAPIView,
    ImageUploadRetrieveUpdateDestroyAPIView,
    EmployeeViewSet,
    RepairOrderViewSet, get_pavilion_choices, PavilionCardRetrieveUpdateDestroyAPIView, current_user_view,
    PavilionStatePieView, OrderBarChartView, OrderMetricsView, available_images_for_order,
)

# Router for employees and repair orders
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'repair-orders', RepairOrderViewSet, basename='repairorder')

urlpatterns = [
    # Images endpoints
    path('images/upload/', upload_images, name='image-upload'),
    path('images/<int:pk>/', ImageUploadRetrieveUpdateDestroyAPIView.as_view(), name='image-detail'),

    # Metadata
    path('districts/', get_districts, name='district-list'),
    path('regions/', get_regions, name='region-list'),

    # Pavilion endpoints
    path('pavilion/', create_pavilion_with_images, name='pavilion-create'),
    path('pavilions/', PavilionCardListCreateAPIView.as_view(), name='pavilion-list'),
    path('pavilions/<int:pk>/', PavilionCardRetrieveUpdateDestroyAPIView.as_view(), name='pavilion-detail'),

    # Predict endpoint
    path('predict/', predict_images, name='predict-images'),

    path('pavilion_choices/', get_pavilion_choices),
    path('me/', current_user_view),

    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('stats/pavilion-states/', PavilionStatePieView.as_view()),
    path('stats/order-bar/', OrderBarChartView.as_view(), name='order-bar'),
    path('stats/order-metrics/', OrderMetricsView.as_view()),
    path('pavilions/<int:pavilion_id>/available_images/', available_images_for_order)

]

# Include router-generated URLs for employees and repair orders
urlpatterns += router.urls

