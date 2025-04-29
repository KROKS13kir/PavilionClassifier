import json
from django.core.management.base import BaseCommand

from classifier.models import District


class Command(BaseCommand):
    help = "Загрузить округа Москвы"

    def handle(self, *args, **kwargs):
        data = [
            { "id": 1, "name": "Восточный", "short": "ВАО" },
            { "id": 2, "name": "Западный", "short": "ЗАО" },
            { "id": 3, "name": "Зеленоградский", "short": "ЗелАО" },
            { "id": 4, "name": "Новомосковский", "short": "НАО" },
            { "id": 5, "name": "Северный", "short": "САО" },
            { "id": 6, "name": "Северо-Восточный", "short": "СВАО" },
            { "id": 7, "name": "Северо-Западный", "short": "СЗАО" },
            { "id": 8, "name": "Троицкий", "short": "ТАО" },
            { "id": 9, "name": "Центральный", "short": "ЦАО" },
            { "id": 10, "name": "Юго-Восточный", "short": "ЮВАО" },
            { "id": 11, "name": "Юго-Западный", "short": "ЮЗАО" },
            { "id": 12, "name": "Южный", "short": "ЮАО" }
        ]

        for item in data:
            district, created = District.objects.get_or_create(
                name=item["name"],
                defaults={"short": item["short"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Добавлен: {district.name}'))
            else:
                self.stdout.write(f'Уже существует: {district.name}')
