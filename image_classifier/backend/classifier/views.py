from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import ImageUpload
from .classifier import predict_image

@api_view(['POST'])
@parser_classes([MultiPartParser])
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
        })

    return Response(results)
