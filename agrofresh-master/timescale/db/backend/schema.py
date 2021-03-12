from django.db import connection
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from timescale.fields import TimescaleDateTimeField


class TimescaleSchemaEditor(DatabaseSchemaEditor):
    # sql_add_hypertable = (
    #     "SELECT create_hypertable("
    #     "{table}, {partition_column}, "
    #     "chunk_time_interval => interval {interval})"
    # )

    # sql_drop_primary_key = (
    #     'ALTER TABLE {table} '
    #     'DROP CONSTRAINT {pkey}'
    # )

    # def drop_primary_key(self, model):
    #     """
    #     Hypertables can't partition if the primary key is not
    #     the partition column.
    #     So we drop the mandatory primary key django creates.
    #     """
    #     db_table = model._meta.db_table
    #     table = self.quote_name(db_table)
    #     pkey = self.quote_name(f'{db_table}_pkey')

    #     sql = self.sql_drop_primary_key.format(table=table, pkey=pkey)

    #     self.execute(sql)

    # def create_hypertable(self, model, field):
    #     """
    #     Create the hypertable with the partition column being the field.
    #     """
    #     partition_column = self.quote_value(field.column)
    #     interval = self.quote_value(field.interval)
    #     table = self.quote_value(model._meta.db_table)

    #     sql = self.sql_add_hypertable.format(
    #         table=table, partition_column=partition_column, interval=interval
    #     )

    #     self.execute(sql)

    # def create_model(self, model):
    #     super().create_model(model)

    #     for field in model._meta.local_fields:
    #         if not isinstance(field, TimescaleDateTimeField):
    #             continue

    #         self.drop_primary_key(model)
    #         self.create_hypertable(model, field)

    def set_telemetry_level(self, level):
        # https://docs.timescale.com/latest/using-timescaledb/telemetry#react-docs

        # get the current user name
        with connection.cursor() as cursor:
            cursor.execute('SELECT current_user')
            current_user = cursor.fetchone()[0]

        # get the current database name
        with connection.cursor() as cursor:
            cursor.execute('SELECT current_catalog')
            current_catalog = cursor.fetchone()[0]

        params = {
            'level': level,
            'current_user': current_user,
            'current_catalog': current_catalog,
        }

        self.execute("ALTER DATABASE %(current_catalog)s SET timescaledb.telemetry_level=%(level)s" % params)
        self.execute("ALTER USER %(current_user)s SET timescaledb.telemetry_level=%(level)s" % params)
        # TODO: fix django.db.utils.InternalError: ALTER SYSTEM cannot run inside a transaction block
        # self.execute("ALTER SYSTEM SET timescaledb.telemetry_level=%(level)s" % params)

    # def set_compression(self, model, interval, segment_by, order_by):
    #     # https://docs.timescale.com/latest/using-timescaledb/compression
    #     # Modifications to chunks that have been compressed are inefficient (or not allowed at all)

    #     # Queries that reference the segmentby columns in the WHERE clause are very efficient
    #     # (all of the primary key columns other than "time" should go into the segmentby list)
    #     # A concrete set of values for each segmentby column should define a "time-series" of
    #     # values you can graph over time.

    #     # Compression is most effective when adjacent data is close in magnitude or exhibits some
    #     # sort of trend. Thus, when compressing data it is important that the order of the input
    #     # data causes it to follow a trend.

    #     raise NotImplementedError("Advanced option")
    #     # TODO validate segment_by, order_by, interval

    #     params = {
    #         "table": model._meta.db_table,
    #         "segment_by":  self.quote_value(segment_by), # 'col1, col2'
    #         "order_by":  self.quote_value(order_by),     # 'col1, col2 DESC'
    #         "interval":  self.quote_value(interval),     # '7 days'
    #     }

    #     sql = """
    #     ALTER TABLE %(table)s SET (
    #         timescaledb.compress,
    #         timescaledb.compress_segmentby = %(segment_by)s,
    #         timescaledb.compress_orderby = %(order_by)s,
    #     );
    #     SELECT add_compress_chunks_policy('%(table)s', INTERVAL %(interval)s);
    #     """

    #     self.execute(sql % params)

    # def def_continuous_aggregate(self, model, interval,
    #     refresh_interval=None,
    #     materialized_only=None,
    #     refresh_lag=None,
    #     ignore_invalidation_older_than=None,
    # ):
    #     params = {
    #         "table": model._meta.db_table,
    #         "view": f"{model._meta.db_table}_summary_{interval.replace(' ', '_')}"
    #         "group_by":  self.quote_value(group_by), # 'col1, col2'
    #         "interval":  self.quote_value(interval), # '1 day'
    #     }

    #     sql = """
    #     CREATE VIEW %(view)s
    #     WITH (timescaledb.continuous) AS
    #     SELECT time_bucket(INTERVAL %(interval)s, time) AS bucket,
    #         %(group_by)s,
    #         AVG(value),
    #         MAX(value),
    #         MIN(value)
    #     FROM %(table)s
    #     GROUP BY %(group_by)s, bucket;
    #     """

    #     self.execute(sql % params)

    #     if materialized_only is not None:
    #         # just get partially aggregated data and not include recent data that has yet to be materialized
    #         params['materialized_only'] = bool(materialized_only)
    #         sql = "ALTER VIEW %(view)s SET (timescaledb.materialized_only = %(materialized_only)s);"
    #         self.execute(sql % params)

    #     if refresh_interval:
    #         # controls how frequently materialization jobs will be launched
    #         params['refresh_interval'] = self.quote_value(refresh_interval)
    #         sql = "ALTER VIEW %(view)s SET (timescaledb.refresh_interval = %(refresh_interval)s);"
    #         self.execute(sql % params)

    #     if refresh_lag:
    #         # controls the balance between the on-the-fly aggregation and pre-computed
    #         # aggregation when querying the continuous aggregate
    #         params['refresh_lag'] = self.quote_value(refresh_lag)
    #         sql = "ALTER VIEW %(view)s SET (timescaledb.refresh_lag = %(refresh_lag)s);"
    #         self.execute(sql % params)

    #     if ignore_invalidation_older_than:
    #         # controls how modifications (inserts, updates, and deletes) will trigger update
    #         # of the continuous aggregate. Modifications with an older time will be ignored
    #         # and not trigger an update of the continuous aggregate.
    #         params['ignore_invalidation_older_than'] = self.quote_value(ignore_invalidation_older_than)
    #         sql = "ALTER VIEW %(view)s SET (timescaledb.ignore_invalidation_older_than = %(ignore_invalidation_older_than)s);"
    #         self.execute(sql % params)

    #     # SELECT * FROM timescaledb_information.continuous_aggregates WHERE view_name = %(view)s;
    #     # DROP VIEW %(view)s CASCADE;

    # def set_retention_policy(self, model, interval):
    #     sql = "SELECT add_drop_chunks_policy(%(table)s, INTERVAL %(interval)s);"

    #     # to only drop raw chunks (while keeping data in the continuous aggregates)
    #     sql = "SELECT add_drop_chunks_policy(%(table)s, INTERVAL %(interval)s, cascade_to_materializations=>FALSE);"