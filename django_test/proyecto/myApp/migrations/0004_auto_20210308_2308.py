# Generated by Django 3.1.6 on 2021-03-08 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0003_auto_20210308_2257'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MiLista',
        ),
        migrations.AlterModelOptions(
            name='contacto',
            options={'verbose_name_plural': 'Contactos'},
        ),
    ]
