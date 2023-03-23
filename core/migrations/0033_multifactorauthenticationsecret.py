# Generated by Django 4.1.7 on 2023-03-22 15:49

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0032_alter_file_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="MultiFactorAuthenticationSecret",
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
                (
                    "uuid",
                    models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
                ),
                ("secret", models.JSONField()),
                ("key", models.JSONField()),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mfa_secret",
                        to="core.rlcuser",
                    ),
                ),
            ],
            options={
                "verbose_name": "MultiFactorAuthenticationSecret",
                "verbose_name_plural": "MultiFactorAuthenticationSecrets",
            },
        ),
    ]
