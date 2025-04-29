from io import BytesIO

from PIL import Image
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import ImageUpload
from .classifier import predict_image
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


# classifier/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import District, Region
from .serializers import DistrictSerializer, RegionSerializer, PavilionCardSerializer


@api_view(['GET'])
def get_districts(request):
    districts = District.objects.all()
    serializer = DistrictSerializer(districts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_regions(request):
    regions = Region.objects.all()
    serializer = RegionSerializer(regions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def upload_images(request):
    files = request.FILES.getlist('images')
    results = []

    for file in files:
        image_instance = ImageUpload.objects.create(image=file)
        predicted_class, confidence = predict_image(image_instance.image.path)

        image_instance.predicted_class = predicted_class
        image_instance.confidence = confidence
        image_instance.save()

        results.append({
            "id": image_instance.id,
            "image": image_instance.image.url,
            "predicted_class": predicted_class,
            "confidence": confidence,
            # Добавим шаблон пустой карточки
            "form": {
                "mpv_code": "",
                "stop_name": "",
                "street": "",
                "district": "",
                "region": "",
                "pavilion_number": "",
                "category": "",
                "pavilion_class": "",
                "balance_holder": "",
                "address": "",
                "confirmed_state": predicted_class,
            }
        })

    return Response(results)


@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def create_pavilion_with_images(request):
    serializer = PavilionCardSerializer(data=request.data, context={'request': request})  # ← передаём request
    if serializer.is_valid():
        pavilion = serializer.save()
        return Response(PavilionCardSerializer(pavilion).data)
    return Response(serializer.errors, status=400)



@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def predict_images(request):
    files = request.FILES.getlist('images')
    results = []

    for file in files:
        image = Image.open(file)  # файл из формы
        predicted_class, confidence = predict_image(image)

        results.append({
            "file_name": file.name,
            "predicted_class": predicted_class,
            "confidence": confidence
        })

    return Response(results)

