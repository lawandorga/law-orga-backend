# Generated by Django 4.1.3 on 2022-12-06 10:33
import uuid

from django.db import migrations


def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model("core", "Record")
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0182_record_uuid"),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
