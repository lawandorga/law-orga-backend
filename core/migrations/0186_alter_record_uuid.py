# Generated by Django 4.1.3 on 2022-12-06 10:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0185_foldersfolder_items"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
    ]
