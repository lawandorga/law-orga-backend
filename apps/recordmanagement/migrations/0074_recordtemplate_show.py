# Generated by Django 3.2.9 on 2021-12-19 21:07

import apps.recordmanagement.models.record
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordmanagement', '0073_alter_recordstatefield_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordtemplate',
            name='show',
            field=models.JSONField(default=apps.recordmanagement.models.record.get_default_show),
        ),
    ]
