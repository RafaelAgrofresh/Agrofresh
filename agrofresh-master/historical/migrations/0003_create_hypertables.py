from django.db import migrations
from timescale.db.migrations import operations
from .. import models


class Migration(migrations.Migration):

    dependencies = [
        ('historical', '0002_enable_timescaledb'),
    ]

    operations = [
        # TODO retention_policy as args (drop_chuncks_older_than:INTERVAL)
        operations.CreateHypertable.from_model(models.Event),
        operations.CreateHypertable.from_model(models.BooleanData),
        operations.CreateHypertable.from_model(models.IntegerData),
        operations.CreateHypertable.from_model(models.FloatData),
    ]
