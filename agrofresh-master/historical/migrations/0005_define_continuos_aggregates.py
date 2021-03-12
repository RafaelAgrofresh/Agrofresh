from django.db import migrations
from timescale.db.migrations import operations
from .. import models

INTERVALS = [
    { 'time_bucket': '1 minute',  'drop_chunks_older_than': '4 months'},
    { 'time_bucket': '5 minutes', 'drop_chunks_older_than': '3 years'},
    { 'time_bucket': '1 hour',    'drop_chunks_older_than': '3 years'},
]

class Migration(migrations.Migration):

    dependencies = [
        ('historical', '0004_enable_compression'),
    ]

    operations = [
        # TODO retention_policy as args -> intervals = list of (time_bucket, retention)
        *operations.DefineContinuousAggregates.from_model(models.IntegerData),
        *operations.DefineContinuousAggregates.from_model(models.FloatData),
    ]
