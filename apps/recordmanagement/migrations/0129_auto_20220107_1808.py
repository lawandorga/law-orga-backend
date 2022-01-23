# Generated by Django 3.2.10 on 2022-01-07 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordmanagement', '0128_remove_poolrecord_yielder'),
    ]

    operations = [
        migrations.RenameField(
            model_name='poolconsultant',
            old_name='enlisted',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='poolrecord',
            old_name='enlisted',
            new_name='created',
        ),
        migrations.AddField(
            model_name='poolconsultant',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='poolrecord',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]