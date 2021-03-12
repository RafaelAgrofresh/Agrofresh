from django.db import migrations
from timescale.db.migrations import operations
from .. import models


# TODO remove migration defined retention policy in Hypertable & ContinuousAggregate defs
class Migration(migrations.Migration):

    dependencies = [
        ('historical', '0005_define_continuos_aggregates'),
    ]

    operations = [
        *operations.DefineDataRetentionPolicies.from_model(models.Event),
        *operations.DefineDataRetentionPolicies.from_model(models.BooleanData),
        *operations.DefineDataRetentionPolicies.from_model(models.IntegerData),
        *operations.DefineDataRetentionPolicies.from_model(models.FloatData),
    ]
