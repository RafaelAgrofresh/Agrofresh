from django.db import migrations
from timescale.db.migrations import operations
from .. import models


class Migration(migrations.Migration):

    dependencies = [
        ('historical', '0003_create_hypertables'),
    ]

    # TODO add time_interval (compress_chunks_older_than: INTERVAL)
    operations = [
        operations.EnableCompression.from_model(models.Event),
        operations.EnableCompression.from_model(models.BooleanData),
        operations.EnableCompression.from_model(models.IntegerData),
        operations.EnableCompression.from_model(models.FloatData),
    ]
