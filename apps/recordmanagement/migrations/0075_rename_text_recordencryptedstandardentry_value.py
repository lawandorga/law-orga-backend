# Generated by Django 3.2.9 on 2021-12-22 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recordmanagement', '0074_recordtemplate_show'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recordencryptedstandardentry',
            old_name='text',
            new_name='value',
        ),
    ]
