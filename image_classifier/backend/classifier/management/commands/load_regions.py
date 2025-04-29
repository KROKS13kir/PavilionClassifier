import os
import json
from django.core.management.base import BaseCommand
from classifier.models import District, Region

class Command(BaseCommand):
    help = "Загрузка районов Москвы и привязка к округам"

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, 'regions.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                regions = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Файл regions.json не найден по пути: {file_path}"))
            return

        for item in regions:
            district_short = item.get("district_short")
            region_name = item.get("name")

            if not district_short or not region_name:
                self.stderr.write(self.style.WARNING(f"Пропущен элемент: {item}"))
                continue

            district, _ = District.objects.get_or_create(short=district_short)
            region, created = Region.objects.get_or_create(name=region_name, district=district)

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Добавлен район: {region_name} ({district_short})"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Уже существует: {region_name}"))
