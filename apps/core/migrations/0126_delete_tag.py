# Generated by Django 4.0.7 on 2022-10-11 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0125_remove_encryptedclient_birthday_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Tag",
        ),
    ]