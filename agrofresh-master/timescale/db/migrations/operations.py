from django.db import connection, migrations, models
from django.db.migrations.operations.base import Operation
from timescale.db.backend.schema import TimescaleSchemaEditor
from itertools import chain


class LoadTimescaleDBExtension(Operation):
    reversible = True

    def __init__(self):
        super().__init__()

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("DROP EXTENSION timescaledb")

    def describe(self):
        return "Creates timescaledb extension if not exists"


class DisableTelemetry(Operation):
    reversible = True

    def __init__(self):
        super().__init__()

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if not isinstance(schema_editor, TimescaleSchemaEditor):
            raise TypeError("TimescaleSchemaEditor expected")

        schema_editor.set_telemetry_level("off")

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if not isinstance(schema_editor, TimescaleSchemaEditor):
            raise TypeError("TimescaleSchemaEditor expected")

        schema_editor.set_telemetry_level("basic")

    def describe(self):
        return "Disable telemetry"


class CreateHypertable(Operation):
    reversible = False

    @classmethod
    def from_model(cls, model, time_column=None, interval=None):
        table = model._meta.db_table
        time_column = time_column or next(
            field.attname
            for field in model._meta.fields
            if isinstance(field, models.DateField)
        )
        return cls(table, time_column, interval)

    def __init__(self, table, time_column, interval=None):
        self.table = table
        self.time_column = time_column
        self.interval = interval
        super().__init__()

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # Hypertables can't partition if the primary key is not the partition column.
        # So we drop the mandatory primary key django creates.
        schema_editor.execute(
            "ALTER TABLE %(table)s DROP CONSTRAINT %(pkey)s" % {
                'table': schema_editor.quote_name(self.table),
                'pkey': schema_editor.quote_name(f'{self.table}_pkey'),
            })

        # FIXME id added in queries
        # # Drop unused primary key column
        # schema_editor.execute(
        #     "ALTER TABLE %(table)s DROP COLUMN %(column)s" % {
        #         'table': schema_editor.quote_name(self.table),
        #         'column': schema_editor.quote_name("id"),
        #     }
        # )

        # TODO add primary key? ALTER TABLE <table> SET PRIMARY KEY (<field, ...>)

        # Creates a TimescaleDB hypertable from a PostgreSQL table (replacing the latter),
        # partitioned on time and with the option to partition on one or more other columns (i.e., space)
        # All actions, such as ALTER TABLE, SELECT, etc., still work on the resulting hypertable.
        schema_editor.execute(
            "SELECT create_hypertable(%(table)s, %(time_column)s)" % {
                'table': schema_editor.quote_value(self.table),
                'time_column': schema_editor.quote_value(self.time_column),
            })

        if self.interval:
            schema_editor.execute(
                "SELECT set_chunk_time_interval(%(table)s, INTERVAL %(interval)s)" % {
                    'table': schema_editor.quote_value(self.table),
                    'interval': schema_editor.quote_value(self.table),
                })


    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        pass # not reversible operation

    def describe(self):
        return f"Create a TimescaleDB hypertable from {self.table}"


class EnableCompression(Operation):
    DEFAULT_COMPRESSION_INTERVAL = '1 day'
    reversible = False

    @classmethod
    def from_model(cls, model, time_column=None, interval=None, segment_by=None, order_by=None):
        table = model._meta.db_table
        time_column = time_column or next(
            field.attname
            for field in model._meta.fields
            if isinstance(field, models.DateField)
        )

        interval = interval or cls.DEFAULT_COMPRESSION_INTERVAL
        if not segment_by:
            segment_by = ', '.join(
                field.attname
                for field in model._meta.fields
                if isinstance(field, models.ForeignKey)
            )

        if not isinstance(segment_by, str):
            raise TypeError("str expected (e.g. 'col1, col2')")

        if not order_by:
            order_by = f"{time_column} DESC"

        if not isinstance(order_by, str):
            raise TypeError("str expected (e.g. 'col1, col2, time DESC')")


        return cls(table, interval, segment_by, order_by)


    def __init__(self, table, interval, segment_by, order_by):
        self.table = table
        self.interval = interval
        self.segment_by = segment_by
        self.order_by = order_by
        super().__init__()

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if not isinstance(schema_editor, TimescaleSchemaEditor):
            raise TypeError("TimescaleSchemaEditor expected")

        # https://docs.timescale.com/latest/using-timescaledb/compression
        # Modifications to chunks that have been compressed are inefficient (or not allowed at all)

        # Queries that reference the segmentby columns in the WHERE clause are very efficient
        # (all of the primary key columns other than "time" should go into the segmentby list)
        # A concrete set of values for each segmentby column should define a "time-series" of
        # values you can graph over time.

        # Compression is most effective when adjacent data is close in magnitude or exhibits some
        # sort of trend. Thus, when compressing data it is important that the order of the input
        # data causes it to follow a trend.

        # TODO validate segment_by, order_by, interval
        params = {
            "table": self.table,
            "segment_by":  schema_editor.quote_value(self.segment_by), # 'col1, col2'
            "order_by":  schema_editor.quote_value(self.order_by),     # 'col1, col2 DESC'
            "interval":  schema_editor.quote_value(self.interval),     # '7 days'
        }

        # turn on compression and set compression options and set a policy
        # by which the system will compress a chunk automatically in the
        # background after it reaches a given age
        schema_editor.execute(
            """ALTER TABLE %(table)s SET (
                timescaledb.compress,
                timescaledb.compress_orderby = %(order_by)s,
                timescaledb.compress_segmentby = %(segment_by)s
            );
            SELECT add_compress_chunks_policy('%(table)s', INTERVAL %(interval)s)""" % params)

        # To see the compression stats:
        # SELECT * FROM timescaledb_information.compressed_chunk_stats;


    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        pass # not reversible operation

    def describe(self):
        return f"Enable compression for {self.table}"


class DefineContinuousAggregates(Operation):
    DEFAULT_AGGREGATION_INTERVALS = ['1 minute', '1 hour', '1 day', '30 days']
    reversible = True

    @classmethod
    def from_model(cls, model, time_column=None, value_column=None, group_by=None, intervals=None):
        table = model._meta.db_table

        time_column = time_column or next(
            field.attname
            for field in model._meta.fields
            if isinstance(field, models.DateField)
        )

        value_column = value_column or next(
            field.attname
            for field in model._meta.fields
            if not isinstance(field, models.AutoField)
            and isinstance(field, (
                models.BooleanField,
                models.IntegerField,
                models.FloatField,
                models.DecimalField,
            ))
        )

        if not group_by:
            group_by = ', '.join(
                field.attname
                for field in model._meta.fields
                if isinstance(field, models.ForeignKey)
            )

        if not isinstance(group_by, str):
            raise TypeError("str expected (e.g. 'col1, col2')")

        intervals = intervals or cls.DEFAULT_AGGREGATION_INTERVALS
        for interval in intervals:
            view = f"{table}_aggregate_{interval.replace(' ', '_')}"
            yield cls(view, table, interval, time_column, value_column, group_by)

    def __init__(self, view, table, interval, time_column, value_column, group_by):
        self.view = view
        self.table = table
        self.interval = interval
        self.time_column = time_column
        self.value_column = value_column
        self.group_by = group_by
        super().__init__()

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # Create Real-time aggregate view
        params = {
            'view': self.view,
            'table': self.table,
            'interval': schema_editor.quote_value(self.interval),
            'time_column': self.time_column,
            'value_column': self.value_column,
            'group_by': self.group_by,
        }

        schema_editor.execute(
            """CREATE VIEW %(view)s
            WITH (timescaledb.continuous, timescaledb.refresh_interval = %(interval)s) AS
            SELECT %(group_by)s,
                MIN(id) AS id,
                time_bucket(INTERVAL %(interval)s, %(time_column)s) AS bucket,
                AVG(%(value_column)s) as %(value_column)s,
                MAX(%(value_column)s) as %(value_column)s_max,
                MIN(%(value_column)s) as %(value_column)s_min
            FROM %(table)s
            GROUP BY %(group_by)s, bucket""" % params)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(
            "DROP VIEW IF EXISTS %(view)s CASCADE" % {
                'view': self.view,
            })

    def describe(self):
        return f"Define continuous aggregates for {self.table} with interval {self.interval}"


class DefineDataRetentionPolicies(Operation):
    reversible = False
    DEFAULT_MODEL_DROP_OLDER_THAN = '1 day'
    DEFAULT_AGGREGATION_DROP_OLDER_THAN = '2 years'

    @classmethod
    def from_model(cls, model):
        table = model._meta.db_table
        yield cls(table, cls.DEFAULT_MODEL_DROP_OLDER_THAN)

        # chunk_time_interval
        with connection.cursor() as cursor:
            prefix = f"{table}_"
            cursor.execute(
                "SELECT view_name FROM timescaledb_information.continuous_aggregates"
                f" WHERE view_name::varchar LIKE '{prefix}%'"
            )

            views  = (row[0] for row in cursor.fetchall())
            for view_name in views:
                interval = view_name.lstrip(prefix).replace('_', ' ')
                yield cls(view_name, cls.DEFAULT_AGGREGATION_DROP_OLDER_THAN)

        # TODO verify that works in the same migration


    def __init__(self, table, interval=None):
        self.table = table
        self.interval = interval
        super().__init__()

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # Create Automatic Data Retention Policy
        params = {
            'table': schema_editor.quote_value(self.table),
            'interval': schema_editor.quote_value(self.interval),
        }

        schema_editor.execute(
            "SELECT add_drop_chunks_policy(%(table)s, INTERVAL %(interval)s)" % params
        )

        # to view scheduled jobs
        # SELECT * FROM timescaledb_information.drop_chunks_policies;


    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # Remove Automatic Data Retention Policy
        params = {
            'table': schema_editor.quote_value(self.table),
        }

        schema_editor.execute(
            "SELECT remove_drop_chunks_policy(%(table)s)" % params
        )

    def describe(self):
        return f"Define data retention policy for {self.table} (drop chuncks older than {self.interval})"