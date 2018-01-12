# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datatrans', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelwordcount',
            name='content_type',
            field=models.OneToOneField(to='contenttypes.ContentType', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
