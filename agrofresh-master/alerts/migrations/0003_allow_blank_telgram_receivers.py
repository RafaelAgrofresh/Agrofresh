# Generated by Django 3.1.6 on 2021-02-09 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0002_alertpermissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramnotificationsettings',
            name='receivers',
            field=models.TextField(blank=True, help_text='Enter receivers IDs (one per line).\nPersonal messages, group chats and channels also available.'),
        ),
    ]
