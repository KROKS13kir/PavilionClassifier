# classifier/serializers.py
from django.utils import timezone
from urllib.request import urlopen

from PIL import Image


from .classifier import predict_image
from .models import District, Region, Employee, RepairOrder, RepairOrderImage

from rest_framework import serializers
from .models import PavilionCard, ImageUpload
from .utils import upload_to_s3, generate_presigned_url


class ImageUploadSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageUpload
        fields = ['id', 'uploaded_at', 'image_url', 'predicted_class', 'confidence', 'confirmed_state']


    def get_image_url(self, obj):
        if obj.image_url:
            return generate_presigned_url(obj.image_url)
        return None



class PavilionCardSerializer(serializers.ModelSerializer):
    images = ImageUploadSerializer(many=True, read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = PavilionCard
        fields = [
            'id', 'mpv_code', 'stop_name', 'street', 'district', 'region',
            'district_name', 'region_name',
            'pavilion_number', 'category', 'pavilion_class',
            'balance_holder', 'address', 'status', 'images', 'requires_repair',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        pavilion = PavilionCard.objects.create(**validated_data)

        images_data = []
        should_require_repair = False

        for key in request.FILES:
            if key.startswith('images['):
                index = key.split('[')[1].split(']')[0]
                image_file = request.FILES[key]
                confirmed_state = request.data.get(f'images[{index}].confirmed_state', '').strip()
                images_data.append({
                    'file': image_file,
                    'confirmed_state': confirmed_state
                })

        for img in images_data:
            s3_key = upload_to_s3(img['file'], img['confirmed_state'])

            with urlopen(generate_presigned_url(s3_key)) as response:
                image = Image.open(response).convert("RGB")
                predicted_class, confidence = predict_image(image)

            # Выбор состояния для логики requires_repair
            state_for_flag = img['confirmed_state'] or predicted_class

            if state_for_flag in ["граффити", "плановый ремонт", "срочный ремонт"]:
                should_require_repair = True

            ImageUpload.objects.create(
                image_url=s3_key,
                confirmed_state=img['confirmed_state'],  # может быть пустым
                predicted_class=predicted_class,
                confidence=confidence,
                pavilion=pavilion
            )

        if should_require_repair:
            pavilion.requires_repair = True
            pavilion.save(update_fields=['requires_repair'])

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

class EmployeeRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'username', 'email', 'password',
            'full_name', 'position', 'district', 'region',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Employee(**validated_data)
        user.set_password(password)
        user.save()
        return user


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        extra_kwargs = {
            'telegram_chat_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Employee(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        # Обрабатываем M2M отдельно
        m2m_fields = []
        for field in instance._meta.many_to_many:
            field_name = field.name
            if field_name in validated_data:
                m2m_fields.append((field_name, validated_data.pop(field_name)))

        # Устанавливаем обычные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        # Устанавливаем many-to-many отдельно
        for field_name, value in m2m_fields:
            getattr(instance, field_name).set(value)

        return instance
    def validate_telegram_chat_id(self, value):
        # заменяем пустую строку на None
        return value or None


class RepairOrderSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        source='employee', write_only=True, queryset=Employee.objects.all()
    )
    image_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    images = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RepairOrder
        fields = [
            'id', 'pavilion', 'employee', 'employee_id',
            'created_at', 'scheduled_for', 'deadline',
            'status', 'description', 'priority', 'completed_at',
            'image_ids', 'images'
        ]
        read_only_fields = ['completed_at']

    def get_images(self, obj):
        return [
            {
                "id": rel.image.id,
                "image_url": generate_presigned_url(rel.image.image_url),
                "uploaded_at": rel.image.uploaded_at,
                "predicted_class": rel.image.predicted_class,
                "confirmed_state": rel.image.confirmed_state,
            }
            for rel in obj.images.select_related('image')
        ]

    def create(self, validated_data):
        image_ids = validated_data.pop('image_ids', [])
        instance = super().create(validated_data)

        # Привязка изображений
        for image_id in image_ids:
            RepairOrderImage.objects.create(repair_order=instance, image_id=image_id)

        return instance

    def update(self, instance, validated_data):
        image_ids = validated_data.pop('image_ids', None)
        previous_status = instance.status

        updated = super().update(instance, validated_data)

        if image_ids is not None:
            # Перепривязываем изображения
            instance.images.all().delete()
            for image_id in image_ids:
                RepairOrderImage.objects.create(repair_order=instance, image_id=image_id)

        # Проставляем дату выполнения
        if previous_status != 'done' and updated.status == 'done' and not updated.completed_at:
            updated.completed_at = timezone.now()
            updated.save(update_fields=['completed_at'])

        # Синхронизация requires_repair
        pavilion = updated.pavilion
        if updated.status == 'done':
            if pavilion.requires_repair:
                pavilion.requires_repair = False
                pavilion.save(update_fields=['requires_repair'])
        else:
            if not pavilion.requires_repair:
                pavilion.requires_repair = True
                pavilion.save(update_fields=['requires_repair'])

        return updated



