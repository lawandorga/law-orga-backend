# Generated by Django 3.2.13 on 2022-06-17 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordmanagement', '0136_recordstatisticfield_helptext'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordencryptionnew',
            name='correct',
            field=models.BooleanField(default=True),
        ),
    ]
