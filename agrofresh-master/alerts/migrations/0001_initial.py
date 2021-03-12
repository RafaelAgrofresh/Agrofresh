# Generated by Django 3.1.6 on 2021-02-05 12:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailNotificationSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=True, help_text='enabled help text', verbose_name='enabled')),
                ('username', models.CharField(max_length=250)),
                ('password', models.CharField(max_length=250)),
                ('host', models.CharField(default='localhost', max_length=250)),
                ('port', models.PositiveSmallIntegerField(default=587, validators=[django.core.validators.MaxValueValidator(65535)])),
                ('use_tls', models.BooleanField(default=True)),
                ('use_ssl', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Email Notification Settings',
                'verbose_name_plural': 'Email Notification Settings',
            },
        ),
        migrations.CreateModel(
            name='TelegramNotificationSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=True, help_text='enabled help text', verbose_name='enabled')),
                ('api_token', models.CharField(help_text='Read more: https://core.telegram.org/bots/api#authorizing-your-bot', max_length=250)),
                ('receivers', models.TextField(help_text='Enter receivers IDs (one per line).\nPersonal messages, group chats and channels also available.')),
            ],
            options={
                'verbose_name': 'Telegram Notification Settings',
                'verbose_name_plural': 'Telegram Notification Settings',
            },
        ),
    ]
