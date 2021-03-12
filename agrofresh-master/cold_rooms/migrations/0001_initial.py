# Generated by Django 3.1.2 on 2020-10-13 09:56

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name help text', max_length=70, verbose_name='name')),
                ('description', models.CharField(help_text='description help text', max_length=200, verbose_name='description')),
            ],
            options={
                'verbose_name': 'zone',
                'verbose_name_plural': 'zones',
                'permissions': (('can_view_zone_params', 'View parameters Zone'), ('can_change_zone_params', 'Change parameters Zones')),
            },
        ),
        migrations.CreateModel(
            name='ColdRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name help text', max_length=70, verbose_name='name')),
                ('description', models.CharField(help_text='description help text', max_length=200, verbose_name='description')),
                ('host', models.GenericIPAddressField(default='127.0.0.1', help_text='modbus slave ip address', verbose_name='ip address')),
                ('port', models.IntegerField(default=502, help_text='tcp port number', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(65535)], verbose_name='port')),
                ('unit', models.IntegerField(default=0, help_text='modbus slave unit identifier (255 if not used)', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(255)], verbose_name='unit identifier')),
                ('address', models.IntegerField(default=40001, help_text='data structure base address', verbose_name='base address')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cold_rooms', to='cold_rooms.zone', verbose_name='zone')),
            ],
            options={
                'verbose_name': 'cold room',
                'verbose_name_plural': 'cold rooms',
                'permissions': (('can_view_cold_room_params', 'View parameters Cold Room'), ('can_change_cold_room_params', 'Change parameters Cold Rooms')),
            },
        ),
    ]