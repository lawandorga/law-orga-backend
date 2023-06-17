# Generated by Django 4.2.2 on 2023-06-17 11:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0055_legalrequirementevent_legal_requirement"),
    ]

    operations = [
        migrations.AlterField(
            model_name="legalrequirementevent",
            name="legal_requirement_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to="core.legalrequirementuser",
            ),
        ),
    ]