# classifier/serializers.py
from urllib.request import urlopen

from PIL import Image
from rest_framework import serializers

from .classifier import predict_image
from .models import District, Region

from rest_framework import serializers
from .models import PavilionCard, ImageUpload
from .utils import upload_to_s3, generate_presigned_url


class ImageUploadSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageUpload
        fields = ['image_url', 'predicted_class', 'confidence', 'confirmed_state']

    def get_image_url(self, obj):
        if obj.image_url:
            return generate_presigned_url(obj.image_url)
        return None



class PavilionCardSerializer(serializers.ModelSerializer):
    images = ImageUploadSerializer(many=True, read_only=True)

    class Meta:
        model = PavilionCard
        fields = [
            'id', 'mpv_code', 'stop_name', 'street', 'district', 'region',
            'pavilion_number', 'category', 'pavilion_class',
            'balance_holder', 'address', 'images'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        pavilion = PavilionCard.objects.create(**validated_data)

        images_data = []

        for key in request.FILES:
            if key.startswith('images['):
                index = key.split('[')[1].split(']')[0]
                image_file = request.FILES[key]
                confirmed_state = request.data.get(f'images[{index}].confirmed_state')
                images_data.append({
                    'file': image_file,
                    'confirmed_state': confirmed_state
                })

        for img in images_data:
            s3_key = upload_to_s3(img['file'], img['confirmed_state'])

            # теперь загружаем обратно для предсказания
            with urlopen(generate_presigned_url(s3_key)) as response:
                image = Image.open(response).convert("RGB")
                predicted_class, confidence = predict_image(image)

            ImageUpload.objects.create(
                image_url=s3_key,
                confirmed_state=img['confirmed_state'],
                predicted_class=predicted_class,
                confidence=confidence,
                pavilion=pavilion
            )

        return pavilion


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']

class RegionSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()

    class Meta:
        model = Region
        fields = ['id', 'name', 'district']
