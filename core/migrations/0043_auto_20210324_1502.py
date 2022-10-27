# Generated by Django 3.1.7 on 2021-03-24 14:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0042_auto_20210324_1439"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="accepted",
        ),
        migrations.AlterField(
            model_name="newuserrequest",
            name="request_from",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="accepted",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]