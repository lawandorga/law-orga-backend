# Generated by Django 3.2.10 on 2021-12-29 17:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recordmanagement', '0100_auto_20211228_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encryptedrecordmessage',
            name='old_record',
            field=models.ForeignKey(blank=True, db_index=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='recordmanagement.encryptedrecord'),
        ),
        migrations.AlterField(
            model_name='encryptedrecordmessage',
            name='record',
            field=models.ForeignKey(db_index=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='recordmanagement.record'),
        ),
        migrations.AlterField(
            model_name='encryptedrecordmessage',
            name='sender',
            field=models.ForeignKey(blank=True, db_index=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='e_record_messages_sent', to=settings.AUTH_USER_MODEL),
        ),
    ]
