# Generated by Django 3.1.2 on 2020-11-05 16:24

import core.models.mixins
from django.db import migrations, models
import django.db.models.deletion
import historical.models.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cold_rooms', '0002_delete_model_zone'),
    ]

    operations = [
        migrations.CreateModel(
            name='FloatDataDownsampled',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.DateTimeField(help_text='timestamp help text', verbose_name='timestamp')),
                ('value', models.FloatField(default=0, help_text='average value description', verbose_name='value')),
                ('min', models.FloatField(default=0, help_text='min value description', verbose_name='min')),
                ('max', models.FloatField(default=0, help_text='max value description', verbose_name='max')),
                ('stddev', models.FloatField(default=0, help_text='stddev value description', verbose_name='stddev')),
            ],
            options={
                'verbose_name': 'float measurement downsampled',
                'verbose_name_plural': 'float measurements downsampled',
                'db_table': 'historical_floatdata_downsampled',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IntegerDataDownsampled',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.DateTimeField(help_text='timestamp help text', verbose_name='timestamp')),
                ('value', models.FloatField(default=0, help_text='average value description', verbose_name='value')),
                ('min', models.FloatField(default=0, help_text='min value description', verbose_name='min')),
                ('max', models.FloatField(default=0, help_text='max value description', verbose_name='max')),
                ('stddev', models.FloatField(default=0, help_text='stddev value description', verbose_name='stddev')),
            ],
            options={
                'verbose_name': 'integer measurement downsampled',
                'verbose_name_plural': 'integer measurements downsampled',
                'db_table': 'historical_integerdata_downsampled',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Alarm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name help text', max_length=70, verbose_name='name')),
                ('enabled', models.BooleanField(default=True, help_text='enabled help text', verbose_name='enabled')),
            ],
            options={
                'verbose_name': 'Alarm',
                'verbose_name_plural': 'Alarms',
            },
            bases=(historical.models.mixins.StructLookUpTableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BooleanData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.DateTimeField(help_text='timestamp help text', verbose_name='timestamp')),
                ('value', models.BooleanField(default=False, help_text='measured value description', verbose_name='value')),
            ],
            options={
                'get_latest_by': 'ts',
                'abstract': False,
            },
            bases=(core.models.mixins.SaveOnValueChangeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.DateTimeField(help_text='timestamp help text', verbose_name='timestamp')),
                ('type', models.CharField(max_length=28)),
                ('meta', models.JSONField(null=True)),
                ('value', models.JSONField(null=True)),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
                'ordering': ('-ts', 'id'),
                'get_latest_by': 'ts',
            },
            bases=(core.models.mixins.InheritanceParentMixin, core.models.mixins.SaveOnValueChangeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name help text', max_length=70, verbose_name='name')),
                ('enabled', models.BooleanField(default=True, help_text='enabled help text', verbose_name='enabled')),
                ('type', models.TextField(choices=[(None, '(Unknown)'), ('bool', 'boolean'), ('int', 'integer'), ('float', 'float')], default='(Unknown)', help_text='type help text', verbose_name='type')),
            ],
            options={
                'abstract': False,
            },
            bases=(historical.models.mixins.StructLookUpTableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name help text', max_length=70, verbose_name='name')),
                ('enabled', models.BooleanField(default=True, help_text='enabled help text', verbose_name='enabled')),
                ('type', models.TextField(choices=[(None, '(Unknown)'), ('bool', 'boolean'), ('int', 'integer'), ('float', 'float')], default='(Unknown)', help_text='type help text', verbose_name='type')),
            ],
            options={
                'verbose_name': 'Parameter',
                'verbose_name_plural': 'Parameters',
            },
            bases=(historical.models.mixins.StructLookUpTableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='IntegerData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.DateTimeField(help_text='timestamp help text', verbose_name='timestamp')),
                ('value', models.IntegerField(default=0, help_text='measured value description', verbose_name='value')),
                ('cold_room', models.ForeignKey(db_index=False, help_text='cold room help text', on_delete=django.db.models.deletion.CASCADE, to='cold_rooms.coldroom', verbose_name='cold room')),
                ('measurement', models.ForeignKey(db_index=False, help_text='measurement help text', on_delete=django.db.models.deletion.CASCADE, to='historical.measurement', verbose_name='measurement')),
            ],
            options={
                'get_latest_by': 'ts',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FloatData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.DateTimeField(help_text='timestamp help text', verbose_name='timestamp')),
                ('value', models.FloatField(default=0.0, help_text='measured value description', verbose_name='value')),
                ('cold_room', models.ForeignKey(db_index=False, help_text='cold room help text', on_delete=django.db.models.deletion.CASCADE, to='cold_rooms.coldroom', verbose_name='cold room')),
                ('measurement', models.ForeignKey(db_index=False, help_text='measurement help text', on_delete=django.db.models.deletion.CASCADE, to='historical.measurement', verbose_name='measurement')),
            ],
            options={
                'get_latest_by': 'ts',
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['-ts', 'id'], name='historical_event_idx'),
        ),
        migrations.AddField(
            model_name='booleandata',
            name='cold_room',
            field=models.ForeignKey(db_index=False, help_text='cold room help text', on_delete=django.db.models.deletion.CASCADE, to='cold_rooms.coldroom', verbose_name='cold room'),
        ),
        migrations.AddField(
            model_name='booleandata',
            name='measurement',
            field=models.ForeignKey(db_index=False, help_text='measurement help text', on_delete=django.db.models.deletion.CASCADE, to='historical.measurement', verbose_name='measurement'),
        ),
        migrations.AddIndex(
            model_name='integerdata',
            index=models.Index(fields=['cold_room', 'measurement', '-ts'], name='historical_integerdata_cidx'),
        ),
        migrations.AddIndex(
            model_name='floatdata',
            index=models.Index(fields=['cold_room', 'measurement', '-ts'], name='historical_floatdata_cidx'),
        ),
        migrations.AddIndex(
            model_name='booleandata',
            index=models.Index(fields=['cold_room', 'measurement', '-ts'], name='historical_booleandata_cidx'),
        ),
    ]