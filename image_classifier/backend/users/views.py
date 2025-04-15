from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer

User = get_user_model()

# 📌 Регистрация (доступна всем)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# 📌 Получение текущего пользователя (доступно только с токеном)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_premium': user.is_premium,
        'full_name': user.full_name,      # ✅ добавь
        'position': user.position,        # ✅ добавь
        'district': user.district,        # ✅ добавь
    })

