#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

# Generated by Django 2.2 on 2019-04-11 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordmanagement', '0002_auto_20190206_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='additional_facts',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='bamf_token',
            field=models.CharField(default='BAMF91293A', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='record',
            name='circumstances',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='consultant_team',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='contact',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='first_consultation',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='first_correspondence',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='foreign_token',
            field=models.CharField(default='JudgeA12', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='record',
            name='lawyer',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='next_steps',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='official_note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='related_persons',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='status_described',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
