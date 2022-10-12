# Generated by Django 4.0.7 on 2022-10-12 09:27

from django.db import migrations, models
import django.db.models.deletion


def migrate_messages(apps, schema_editor):
    EncryptedRecordMessage = apps.get_model("core", "EncryptedRecordMessage")

    for m in list(EncryptedRecordMessage.objects.all()):
        m.sender = m.sender_old.rlc_user
        m.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0128_rename_sender_encryptedrecordmessage_sender_old'),
    ]

    operations = [
        migrations.AddField(
            model_name='encryptedrecordmessage',
            name='sender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='core.rlcuser'),
        ),
        migrations.RunPython(migrate_messages)
    ]
