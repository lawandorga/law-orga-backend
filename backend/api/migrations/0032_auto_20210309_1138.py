# Generated by Django 3.0 on 2021-03-09 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0031_auto_20201103_0943"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="type",
            field=models.CharField(
                choices=[
                    ("RECORD__CREATED", "RECORD__CREATED"),
                    ("RECORD__UPDATED", "RECORD__UPDATED"),
                    ("RECORD__DELETED", "RECORD__DELETED"),
                    ("RECORD__RECORD_MESSAGE_ADDED", "RECORD__RECORD_MESSAGE_ADDED"),
                    ("RECORD__RECORD_DOCUMENT_ADDED", "RECORD__RECORD_DOCUMENT_ADDED"),
                    (
                        "RECORD__RECORD_DOCUMENT_MODIFIED",
                        "RECORD__RECORD_DOCUMENT_MODIFIED",
                    ),
                    ("RECORD__CLIENT_UPDATE", "RECORD__CLIENT_UPDATE"),
                    ("RECORD__NEW_RECORD_PERMISSION", "RECORD__NEW_RECORD_PERMISSION"),
                    ("RECORD__ACCESS_GRANTED", "RECORD__ACCESS_GRANTED"),
                    ("RECORD__ACCESS_DENIED", "RECORD__ACCESS_DENIED"),
                    (
                        "RECORD__DELETION_REQUEST_DENIED",
                        "RECORD__DELETION_REQUEST_DENIED",
                    ),
                    ("RECORD__DOCUMENT_DELETED", "RECORD__DOCUMENT_DELETED"),
                    (
                        "RECORD__DOCUMENT_DELETION_REQUEST_DENIED",
                        "RECORD__DOCUMENT_DELETION_REQUEST_DECLINED",
                    ),
                    (
                        "RECORD_PERMISSION_REQUEST__REQUESTED",
                        "RECORD_PERMISSION_REQUEST__REQUESTED",
                    ),
                    (
                        "RECORD_PERMISSION_REQUEST__ACCEPTED",
                        "RECORD_PERMISSION_REQUEST__ACCEPTED",
                    ),
                    (
                        "RECORD_PERMISSION_REQUEST__DECLINED",
                        "RECORD_PERMISSION_REQUEST__DECLINED",
                    ),
                    (
                        "RECORD_DELETION_REQUEST__REQUESTED",
                        "RECORD_DELETION_REQUEST__REQUESTED",
                    ),
                    (
                        "RECORD_DELETION_REQUEST__ACCEPTED",
                        "RECORD_DELETION_REQUEST__ACCEPTED",
                    ),
                    (
                        "RECORD_DELETION_REQUEST__DECLINED",
                        "RECORD_DELETION_REQUEST__DECLINED",
                    ),
                    ("USER_REQUEST__REQUESTED", "USER_REQUEST__REQUESTED"),
                    ("USER_REQUEST__ACCEPTED", "USER_REQUEST__ACCEPTED"),
                    ("USER_REQUEST__DECLINED", "USER_REQUEST__DECLINED"),
                    (
                        "RECORD_DOCUMENT_DELETION_REQUEST__REQUESTED",
                        "RECORD_DOCUMENT_DELETION_REQUEST__REQUESTED",
                    ),
                    (
                        "RECORD_DOCUMENT_DELETION_REQUEST__ACCEPTED",
                        "RECORD_DOCUMENT_DELETION_REQUEST__ACCEPTED",
                    ),
                    (
                        "RECORD_DOCUMENT_DELETION_REQUEST__DECLINED",
                        "RECORD_DOCUMENT_DELETION_REQUEST__DECLINED",
                    ),
                    ("GROUP__ADDED_ME", "GROUP__ADDED_ME"),
                    ("GROUP__REMOVED_ME", "GROUP__REMOVED_ME"),
                    ("FILE__UPLOAD_ERROR", "FILE__UPLOAD_ERROR"),
                    ("FOLDER__FILE_NOT_EXISTING", "FOLDER__FILE_NOT_EXISTING"),
                    ("FOLDER__FILE_UPLOAD_ERROR", "FOLDER__FILE_UPLOAD_ERROR"),
                ],
                default="",
                max_length=75,
            ),
        ),
        migrations.AlterField(
            model_name="notificationgroup",
            name="type",
            field=models.CharField(
                choices=[
                    ("RECORD", "RECORD"),
                    ("RECORD_PERMISSION_REQUEST", "RECORD_PERMISSION_REQUEST"),
                    ("RECORD_DELETION_REQUEST", "RECORD_DELETION_REQUEST"),
                    (
                        "RECORD_DOCUMENT_DELETION_REQUEST",
                        "RECORD_DOCUMENT_DELETION_REQUEST",
                    ),
                    ("USER_REQUEST", "USER_REQUEST"),
                    ("GROUP", "GROUP"),
                    ("FILE", "FILE"),
                    ("FOLDER", "FOLDER"),
                ],
                max_length=100,
            ),
        ),
    ]
