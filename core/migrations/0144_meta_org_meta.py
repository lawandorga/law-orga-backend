# Generated by Django 4.1.3 on 2022-11-11 07:38

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0143_alter_legalrequirementuser_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="Meta",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slug", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("name", models.CharField(max_length=1000)),
            ],
            options={
                "verbose_name": "Meta",
                "verbose_name_plural": "Metas",
            },
        ),
        migrations.AddField(
            model_name="org",
            name="meta",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="core.meta"
            ),
        ),
    ]