# Generated by Django 4.1.4 on 2022-12-30 12:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_alter_legalrequirement_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="encryptedrecordmessage",
            name="folder_uuid",
            field=models.UUIDField(null=True),
        ),
    ]
