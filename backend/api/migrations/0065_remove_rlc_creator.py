# Generated by Django 3.1.6 on 2021-06-09 18:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0064_rlc_use_record_pool'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rlc',
            name='creator',
        ),
    ]
