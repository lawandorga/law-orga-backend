# Generated by Django 4.0.7 on 2022-10-22 18:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0118_alter_rlcuser_org"),
    ]

    operations = [
        migrations.CreateModel(
            name="MatrixUser",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False, max_length=8, primary_key=True, serialize=False
                    ),
                ),
                ("_group", models.CharField(blank=True, max_length=255, null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="matrix_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "MatrixUser",
                "verbose_name_plural": "MatrixUsers",
                "ordering": ["user__name"],
            },
        ),
    ]