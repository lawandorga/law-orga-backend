# Generated by Django 3.1.7 on 2021-04-02 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0054_auto_20210330_1721"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="userprofile",
            options={
                "ordering": ["name"],
                "verbose_name": "UserProfile",
                "verbose_name_plural": "UserProfiles",
            },
        ),
        migrations.AlterField(
            model_name="group", name="name", field=models.CharField(max_length=200),
        ),
    ]
