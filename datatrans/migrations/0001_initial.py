# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldWordCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_words', models.IntegerField(default=0)),
                ('valid', models.BooleanField(default=False)),
                ('field', models.CharField(max_length=64, db_index=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KeyValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(default=None, null=True)),
                ('field', models.CharField(max_length=255)),
                ('language', models.CharField(db_index=True, max_length=5, choices=[(b'nl-be', b'NL'), (b'fr-be', b'FR'), (b'en-be', b'EN'), (b'nl-nl', b'NL'), (b'en-nl', b'EN'), (b'pl-pl', b'PL'), (b'en-pl', b'PL')])),
                ('value', models.TextField(blank=True)),
                ('edited', models.BooleanField(default=False)),
                ('fuzzy', models.BooleanField(default=False)),
                ('digest', models.CharField(max_length=40, db_index=True)),
                ('updated', models.DateTimeField(default=datetime.datetime.now, auto_now=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModelWordCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_words', models.IntegerField(default=0)),
                ('valid', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='keyvalue',
            unique_together=set([('language', 'content_type', 'field', 'object_id', 'digest')]),
        ),
        migrations.AlterUniqueTogether(
            name='fieldwordcount',
            unique_together=set([('content_type', 'field')]),
        ),
    ]
