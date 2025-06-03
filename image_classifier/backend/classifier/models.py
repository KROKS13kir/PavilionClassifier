# image_classifier/models.py
import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from classifier.utils import delete_from_s3


# classifier/models.py
class District(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short = models.CharField(max_length=20, unique=True)




class Region(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='regions')

    class Meta:
        unique_together = ('name', 'district')  # ✅ Уникальность пары (name, district)
        verbose_name = "Район"
        verbose_name_plural = "Районы"

    def __str__(self):
        return f"{self.district.name} — {self.name}"


class PavilionCard(models.Model):
    mpv_code = models.CharField(max_length=100)
    stop_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    pavilion_number = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=[("Павильон нового типа", "Павильон нового типа"),
                                                         ("Павильон старого типа", "Павильон старого типа"),
                                                         ("Павильон инн. типа", "Павильон инн. типа"),
                                                         ("Белый пилон", "Белый пилон"),
                                                         ("Черный пилон", "Черный пилон"),
                                                         ("Флаг", "Флаг"),
                                                         ("Информационное табло", "Информационное табло"),
                                                         ])
    pavilion_class = models.CharField(max_length=100)
    balance_holder = models.CharField(max_length=100, choices=[("Мосгортранс", "Мосгортранс"), ("Московский Метрополитен", "Московский Метрополитен")])
    address = models.TextField(blank=True)
    status = models.CharField(max_length=100, choices=[("Баланс", "Баланс"),
                                                                ("До приемки", "До приемки"),
                                                                ("Планируемый", "Планируемый"),
                                                                ("Принят комп.", "Принят комп."),
                                                                ("Тех. приемка", "Тех. приемка"),
                                                                ])
    requires_repair = models.BooleanField(default=False)


class ImageUpload(models.Model):
    image_url = models.CharField(max_length=500)  # теперь просто ссылка, а не ImageField
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    predicted_class = models.CharField(max_length=100, blank=True, null=True)
    confidence = models.FloatField(null=True, blank=True)
    confirmed_state = models.CharField(max_length=100, blank=True)
    pavilion = models.ForeignKey('PavilionCard', on_delete=models.CASCADE, related_name='images', null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.image_url:
            try:
                delete_from_s3(self.image_url)
            except Exception as e:
                print(f"⚠️ Ошибка при удалении из S3: {e}")
        super().delete(*args, **kwargs)


from django.db import models
import uuid


class EmployeeManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Имя пользователя обязательно")

        # Преобразование ID округа в объект, если пришёл числовой ID
        district = extra_fields.get("district")
        if isinstance(district, int):
            try:
                extra_fields["district"] = District.objects.get(pk=district)
            except District.DoesNotExist:
                raise ValueError("Округ с таким ID не найден")

        user = self.model(username=username, **extra_fields)

        if password:
            user.set_password(password)
        else:
            raise ValueError("Пароль обязателен")

        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        extra_fields.setdefault('full_name', 'Администратор')
        extra_fields.setdefault('position', 'Администратор')

        if not extra_fields.get('district'):
            district = District.objects.first()
            if not district:
                raise ValueError("Нет ни одного округа. Создай его перед этим.")
            extra_fields['district'] = district

        return self.create_user(username, password, **extra_fields)

    # 🔧 Обязательный метод для createsuperuser
    def get_by_natural_key(self, username):
        return self.get(username=username)

class Employee(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, blank=True, null=True, unique=True)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    full_name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    district = models.ForeignKey('District', on_delete=models.PROTECT)
    region = models.ForeignKey('Region', on_delete=models.PROTECT, null=True, blank=True)

    telegram_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    telegram_chat_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=True
    )

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name', 'position', 'district']

    objects = EmployeeManager()

    def __str__(self):
        return f"{self.full_name} ({self.position})"

class RepairOrder(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('assigned', 'Назначен'),
        ('in_progress', 'В работе'),
        ('done', 'Выполнен'),
    ]

    pavilion = models.ForeignKey(
        'PavilionCard',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    description = models.TextField(blank=True)
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    deadline = models.DateField(null=True, blank=True)  # Срок, назначенный сотруднику
    completed_at = models.DateTimeField(null=True, blank=True)  # Дата фактического выполнения

    def __str__(self):
        return f"Order #{self.id} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        # сначала сохраняем сам наряд
        super().save(*args, **kwargs)

        # затем синхронизируем флаг в pavilion
        pav = self.pavilion
        if self.status == 'done':
            if pav.requires_repair:
                pav.requires_repair = False
                pav.save(update_fields=['requires_repair'])
        else:
            if not pav.requires_repair:
                pav.requires_repair = True
                pav.save(update_fields=['requires_repair'])


class RepairOrderImage(models.Model):
    repair_order = models.ForeignKey('RepairOrder', on_delete=models.CASCADE, related_name='images')
    image = models.ForeignKey('ImageUpload', on_delete=models.CASCADE, related_name='repair_orders')

    class Meta:
        unique_together = ('repair_order', 'image')

