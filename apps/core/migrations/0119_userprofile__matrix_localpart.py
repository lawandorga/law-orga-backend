# Generated by Django 4.0.7 on 2022-09-30 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0118_alter_rlcuser_org'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='_matrix_localpart',
            field=models.CharField(max_length=8, null=True, unique=True),
        ),
    ]
