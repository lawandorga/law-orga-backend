# Generated by Django 3.1.6 on 2021-06-01 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0007_file_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='key',
            field=models.SlugField(allow_unicode=True, max_length=200, null=True, unique=True),
        ),
    ]
