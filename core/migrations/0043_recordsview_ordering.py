# Generated by Django 4.1.7 on 2023-03-27 16:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0042_recordsview_org_alter_recordsview_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="recordsview",
            name="ordering",
            field=models.IntegerField(default=0),
        ),
    ]
