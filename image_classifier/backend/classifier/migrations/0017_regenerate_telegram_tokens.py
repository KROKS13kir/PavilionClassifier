from django.db import migrations
import uuid

def regenerate_all_tokens(apps, schema_editor):
    Employee = apps.get_model("classifier", "Employee")
    for emp in Employee.objects.all():
        emp.telegram_token = uuid.uuid4()
        emp.save(update_fields=["telegram_token"])

class Migration(migrations.Migration):
    dependencies = [
        ("classifier", "0015_alter_employee_telegram_token"),
    ]
    operations = [
        migrations.RunPython(regenerate_all_tokens, reverse_code=migrations.RunPython.noop),
    ]