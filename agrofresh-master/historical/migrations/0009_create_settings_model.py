# Generated by Django 3.1.6 on 2021-03-04 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('historical', '0008_custom_views_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_unack_alarms', models.BooleanField(default=True, help_text='Show unacknowledged and active alarms, or only active', verbose_name='Show unacknowledged alarms')),
            ],
            options={
                'verbose_name': 'Settings',
                'verbose_name_plural': 'Settings',
            },
        ),
    ]
