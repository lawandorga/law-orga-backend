# Generated by Django 4.0.7 on 2022-10-12 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0131_remove_loggedpath_data"),
    ]

    operations = [
        migrations.RenameField(
            model_name="recordusersentry",
            old_name="value",
            new_name="value_old",
        ),
    ]
