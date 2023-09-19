# Generated by Django 5.0a1 on 2023-09-19 13:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0058_remove_legalrequirement_rlc_users_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimelineFollowUp",
            fields=[
                ("uuid", models.UUIDField(primary_key=True, serialize=False)),
                ("text_enc", models.JSONField(default=dict)),
                ("title_enc", models.JSONField(default=dict)),
                ("time", models.DateTimeField()),
                ("folder_uuid", models.UUIDField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "org",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="timeline_follow_ups",
                        to="core.org",
                    ),
                ),
            ],
        ),
    ]
