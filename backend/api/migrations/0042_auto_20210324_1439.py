# Generated by Django 3.1.7 on 2021-03-24 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20210324_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='accepted',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='email_confirmed',
            field=models.BooleanField(default=True),
        ),
    ]
