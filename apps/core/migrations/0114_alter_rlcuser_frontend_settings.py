# Generated by Django 4.0.7 on 2022-09-23 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0113_rlcuser_frontend_settings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rlcuser",
            name="frontend_settings",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
