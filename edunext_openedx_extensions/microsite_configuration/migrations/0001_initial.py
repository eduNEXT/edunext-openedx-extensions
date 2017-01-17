# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalMicrositeOrganizationMapping',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('organization', models.CharField(max_length=63, db_index=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical microsite organization mapping',
            },
        ),
        migrations.CreateModel(
            name='HistoricalMicrositeTemplate',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('template_uri', models.CharField(max_length=255, db_index=True)),
                ('template', models.TextField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical microsite template',
            },
        ),
        migrations.CreateModel(
            name='Microsite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=63, db_index=True)),
                ('values', jsonfield.fields.JSONField(blank=True)),
                ('subdomain', models.CharField(max_length=127, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='MicrositeOrganizationMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('organization', models.CharField(unique=True, max_length=63, db_index=True)),
                ('microsite', models.ForeignKey(to='microsite_configuration.Microsite')),
            ],
        ),
        migrations.CreateModel(
            name='MicrositeTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('template_uri', models.CharField(max_length=255, db_index=True)),
                ('template', models.TextField()),
                ('microsite', models.ForeignKey(to='microsite_configuration.Microsite')),
            ],
        ),
        migrations.AddField(
            model_name='historicalmicrositetemplate',
            name='microsite',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='microsite_configuration.Microsite', null=True),
        ),
        migrations.AddField(
            model_name='historicalmicrositeorganizationmapping',
            name='microsite',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='microsite_configuration.Microsite', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='micrositetemplate',
            unique_together=set([('microsite', 'template_uri')]),
        ),
    ]
