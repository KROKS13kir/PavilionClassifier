from django.db import migrations
import uuid

def generate_unique_tokens(apps, schema_editor):
    Employee = apps.get_model("classifier", "Employee")
    for emp in Employee.objects.filter(telegram_token__isnull=True):
        emp.telegram_token = uuid.uuid4()
        emp.save(update_fields=["telegram_token"])

class Migration(migrations.Migration):
    dependencies = [
        ("classifier", "0013_employee_telegram_chat_id"),  # замените на вашу 0013
    ]
    operations = [
        migrations.RunPython(generate_unique_tokens, reverse_code=migrations.RunPython.noop),
    ]