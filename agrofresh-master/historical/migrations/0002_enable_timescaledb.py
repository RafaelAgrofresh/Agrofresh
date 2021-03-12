from django.db import migrations
from timescale.db.migrations import operations
from .. import models


class Migration(migrations.Migration):

    dependencies = [
        ('historical', '0001_initial'),
    ]

    operations = [
        operations.LoadTimescaleDBExtension(),
        operations.DisableTelemetry(),
    ]
