from datetime import datetime, timedelta, timezone
from urllib.request import urlopen
from PIL import Image
from django.http import JsonResponse
from django.utils.timezone import make_aware
from rest_framework import generics, permissions, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from .models import ImageUpload, PavilionCard, Employee, RepairOrder
from .classifier import predict_image
from rest_framework.decorators import parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS

# classifier/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import District, Region
from .serializers import DistrictSerializer, RegionSerializer, PavilionCardSerializer, ImageUploadSerializer, \
    EmployeeSerializer, RepairOrderSerializer
from .utils import generate_presigned_url, upload_to_s3


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
    files  = request.FILES.getlist('images')
    states = request.data.getlist('confirmed_states')
    pav_id = request.data.get('pavilion')

    try:
        pavilion = PavilionCard.objects.get(id=pav_id)
    except PavilionCard.DoesNotExist:
        return Response({'error': 'Pavilion not found'}, status=404)

    results = []
    should_require_repair = pavilion.requires_repair

    for idx, file in enumerate(files):
        confirmed = states[idx].strip() if idx < len(states) else ''

        # 1. Загрузка в S3
        s3_key = upload_to_s3(file, confirmed)
        presigned_url = generate_presigned_url(s3_key)

        # 2. Предсказание
        with urlopen(presigned_url) as resp:
            img = Image.open(resp).convert("RGB")
            pred_cls, conf = predict_image(img)

        # 3. Определяем, на что ориентироваться
        state_for_flag = confirmed or pred_cls
        if state_for_flag in ["граффити", "плановый ремонт", "срочный ремонт"]:
            should_require_repair = True

        # 4. Сохраняем изображение
        inst = ImageUpload.objects.create(
            image_url       = s3_key,
            predicted_class = pred_cls,
            confidence      = conf,
            confirmed_state = confirmed,
            pavilion        = pavilion
        )

        results.append({
            'id':               inst.id,
            'image_url':        presigned_url,
            'predicted_class':  pred_cls,
            'confidence':       conf,
            'confirmed_state':  confirmed,
        })

    if should_require_repair and not pavilion.requires_repair:
        pavilion.requires_repair = True
        pavilion.save(update_fields=["requires_repair"])

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

class PavilionCardListCreateAPIView(generics.ListCreateAPIView):
    queryset = PavilionCard.objects.all().prefetch_related('images')
    serializer_class = PavilionCardSerializer
    permission_classes = [permissions.IsAuthenticated]

class ImageUploadRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ImageUpload.objects.all()
    serializer_class = ImageUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

class PavilionCardRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PavilionCard.objects.all().prefetch_related('images')
    serializer_class = PavilionCardSerializer
    permission_classes = [permissions.IsAuthenticated]

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        # Пароль обрабатывается через serializer.create()
        serializer.save()

    def perform_update(self, serializer):
        # Пароль обрабатывается через serializer.update()
        serializer.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'position': user.position,
        'is_superuser': user.is_superuser,
        'district_name': user.district.name if user.district else None,
    })


class RepairOrderViewSet(viewsets.ModelViewSet):
    queryset         = RepairOrder.objects.select_related('pavilion','employee')
    serializer_class = RepairOrderSerializer
    permission_classes = [IsAuthenticated]

def get_pavilion_choices(request):
    return JsonResponse({
        "category": PavilionCard._meta.get_field("category").choices,
        "balance_holder": PavilionCard._meta.get_field("balance_holder").choices,
        "status": PavilionCard._meta.get_field("status").choices,
    })

from django.db.models import Max, Count, OuterRef, Exists, Q, F, ExpressionWrapper, DurationField, Avg


class PavilionStatePieView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        district_id = request.query_params.get('district')
        region_id = request.query_params.get('region')
        state_filter = request.query_params.get('state')

        if not date_from or not date_to:
            return Response({"error": "Укажите начало и конец периода"}, status=400)

        try:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Неверный формат даты"}, status=400)

        query = PavilionCard.objects.all()
        if district_id:
            query = query.filter(district_id=district_id)
        if region_id:
            query = query.filter(region_id=region_id)

        states = {
            "не требует ремонта": 0,
            "граффити": 0,
            "плановый ремонт": 0,
            "срочный ремонт": 0,
        }

        for pavilion in query:
            # Находим дату последних изображений в пределах периода
            latest_date = pavilion.images.filter(
                uploaded_at__date__range=(date_from, date_to)
            ).aggregate(latest=Max('uploaded_at'))['latest']

            if not latest_date:
                continue

            date_only = latest_date.date()

            images = pavilion.images.filter(uploaded_at__date=date_only)

            confirmed = list(images.values_list("confirmed_state", flat=True))

            if all(s == "не требует ремонта" for s in confirmed):
                states["не требует ремонта"] += 1
            elif "срочный ремонт" in confirmed:
                states["срочный ремонт"] += 1
            elif "плановый ремонт" in confirmed:
                states["плановый ремонт"] += 1
            elif "граффити" in confirmed:
                states["граффити"] += 1

        if state_filter:
            states = {k: v for k, v in states.items() if k == state_filter}

        return Response(states)


class OrderBarChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        district_id = request.query_params.get('district')
        region_id = request.query_params.get('region')
        state_filter = request.query_params.get('state')
        show_overdue = request.query_params.get('overdue') == 'true'

        try:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return Response({"error": "Неверный формат дат"}, status=400)

        # Базовый фильтр
        base_filter = Q(created_at__date__range=(date_from, date_to))

        if district_id:
            base_filter &= Q(pavilion__district_id=district_id)
        if region_id:
            base_filter &= Q(pavilion__region_id=region_id)

        if state_filter:
            pavilion_ids = ImageUpload.objects.filter(
                confirmed_state=state_filter,
                uploaded_at__date__range=(date_from, date_to)
            ).values_list('pavilion_id', flat=True).distinct()
            base_filter &= Q(pavilion_id__in=pavilion_ids)

        # Всего нарядов (все, независимо от статуса)
        total_qs = RepairOrder.objects.filter(base_filter) \
            .values('employee__full_name') \
            .annotate(total=Count('id'))
        total_map = {r['employee__full_name']: r['total'] for r in total_qs}

        # Выполненные (done)
        done_qs = RepairOrder.objects.filter(base_filter & Q(status='done')) \
            .values('employee__full_name') \
            .annotate(done=Count('id'))
        done_map = {r['employee__full_name']: r['done'] for r in done_qs}

        # Просроченные (только выполненные с нарушением срока)
        overdue_qs = RepairOrder.objects.filter(
            base_filter & Q(status='done') & Q(completed_at__date__gt=F('deadline'))
        ).values('employee__full_name').annotate(overdue=Count('id'))
        overdue_map = {r['employee__full_name']: r['overdue'] for r in overdue_qs}

        result = []

        for name in total_map:
            result.append({
                "name": name,
                "done": done_map.get(name, 0),
                "overdue": overdue_map.get(name, 0),
                "total": total_map.get(name, 0)
            })

        return Response(result)


class OrderMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        state_filter = request.query_params.get('state')
        district_id = request.query_params.get('district')
        region_id = request.query_params.get('region')

        try:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return Response({"error": "Неверный формат дат"}, status=400)

        orders = RepairOrder.objects.filter(
            status='done',
            completed_at__date__range=(date_from, date_to)
        ).select_related('employee', 'pavilion')

        if district_id:
            orders = orders.filter(pavilion__district_id=district_id)
        if region_id:
            orders = orders.filter(pavilion__region_id=region_id)
        if state_filter:
            orders = orders.filter(
                pavilion__images__confirmed_state=state_filter
            ).distinct()

        top_employee = (
            orders.values('employee__full_name')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')
            .first()
        )

        fastest = []
        durations = []
        overdue_days = []

        for order in orders:
            if order.completed_at and order.scheduled_for:
                # Приводим к timezone-aware
                scheduled_dt = make_aware(datetime.combine(order.scheduled_for, datetime.min.time()))

                delta = order.completed_at - scheduled_dt
                durations.append(delta)

                if order.deadline:
                    # Просрочка только если позже deadline
                    late_days = (order.completed_at.date() - order.deadline).days
                    overdue_days.append(max(0, late_days))

                fastest.append({
                    'name': order.employee.full_name,
                    'duration': delta
                })

        # Средняя продолжительность выполнения
        if durations:
            total_seconds = sum(d.total_seconds() for d in durations)
            avg_duration = timedelta(seconds=total_seconds / len(durations))
            avg_duration_str = f"{avg_duration.days} дн. {avg_duration.seconds // 3600} ч."
        else:
            avg_duration_str = "—"

        avg_overdue = round(sum(overdue_days) / len(overdue_days)) if overdue_days else 0

        fastest_employee = None
        if fastest:
            fastest.sort(key=lambda x: x['duration'])
            fastest_employee = fastest[0]['name']

        return Response({
            "top_employee": top_employee['employee__full_name'] if top_employee else None,
            "fastest_employee": fastest_employee,
            "avg_completion_time": avg_duration_str,
            "avg_overdue_days": avg_overdue
        })


@api_view(['GET'])
def available_images_for_order(request, pavilion_id):
    last_order = RepairOrder.objects.filter(pavilion_id=pavilion_id).order_by('-created_at').first()
    last_date = last_order.created_at if last_order else None

    images_qs = ImageUpload.objects.filter(pavilion_id=pavilion_id)
    if last_date:
        images_qs = images_qs.filter(uploaded_at__gt=last_date)

    # ✅ Сериализуем через ImageUploadSerializer с подписанными ссылками
    serializer = ImageUploadSerializer(images_qs, many=True, context={'request': request})
    return Response(serializer.data)
