# Generated by Django 5.0.2 on 2024-03-13 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0095_alter_mailimport_options_alter_mailimport_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="datasheet",
            name="folder_uuid",
            field=models.UUIDField(db_index=True),
        ),
    ]