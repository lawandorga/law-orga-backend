# Generated by Django 4.0.7 on 2022-10-12 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0130_remove_encryptedrecordmessage_sender_old"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="loggedpath",
            name="data",
        ),
    ]
