## Disable telemetry
```sql
ALTER [SYSTEM | DATABASE | USER] { *db_name* | *role_specification* } SET timescaledb.telemetry_level=off
```

## Backup database
```sh
pg_dump -Fc -f <dbname>.bak <dbname>
```

## Restore database
```sql
CREATE DATABASE <dbname>;
\c <dbname> --connect to the db where we'll perform the restore
CREATE EXTENSION timescaledb;
SELECT timescaledb_pre_restore();

-- execute the restore (or from a shell)
\! pg_restore -Fc -d <dbname> <dbname>.bak

SELECT timescaledb_post_restore();
```

## Continuous Aggregates
Given the hypertable:
```sql
CREATE TABLE conditions (
      time TIMESTAMPTZ NOT NULL,
      device INTEGER NOT NULL,
      temperature FLOAT NOT NULL,
      PRIMARY KEY(time, device)
);
SELECT create_hypertable('conditions', 'time');
```

to create a continuous aggregate:
```sql
CREATE VIEW conditions_summary_hourly
WITH (timescaledb.continuous) AS
SELECT device,
       time_bucket(INTERVAL '1 hour', time) AS bucket,
       AVG(temperature),
       MAX(temperature),
       MIN(temperature)
FROM conditions
GROUP BY device, bucket;

ALTER VIEW conditions_summary_hourly SET (timescaledb.refresh_interval = '15 min');
```

## Data Retention
```sql
-- collect raw data into chunks of one day
SELECT create_hypertable('conditions', 'time', chunk_time_interval => INTERVAL '1 day');

-- drop all chunks from the hypertable that only include data **older** than 24h
-- and not delete any individual rows of data in chunks
SELECT drop_chunks(INTERVAL '24 hours', 'conditions');
```

### Data Retention with Continuous Aggregates

To only remove chunks from the hypertable conditions and not cascade to dropping chunks on the continuous aggregate conditions_summary_daily
```sql
ALTER VIEW conditions_summary_daily SET (
   timescaledb.ignore_invalidation_older_than = '29 days'
);

SELECT drop_chunks(INTERVAL '30 days', 'conditions', cascade_to_materialization => FALSE);
SELECT drop_chunks(INTERVAL '1 year', 'conditions_summary_daily');
```

### Automatic Data Retention Policies

```sql
-- add retention policy to discard chunks older than 24 hours
SELECT add_drop_chunks_policy('conditions', INTERVAL '24 hours');

-- remove retention policy
SELECT remove_drop_chunks_policy('conditions');
```


```py
# Narrow-table vs Wide-table model

# TimescaleDB
time = models.DateTimeField(auto_now_add=True, primary_key=True)
# # CREATE TABLE table1 (
# #  time        TIMESTAMPTZ       NOT NULL,
# #  ...
# # );

# Create Hypertables
# Read https://docs.timescale.com/latest/api#create_hypertable
# Read https://docs.djangoproject.com/en/3.0/topics/db/sql/
from django.db import connection

def execute_sql(query):
    with connection.cursor() as cursor:
    # or connections['my_db_alias'].cursor() if more than one db
      cursor.execute(query)
      result = cursor.fetchall()
      return result

execute_sql("SELECT create_hypertable('table1', 'time')")
execute_sql("SELECT create_hypertable('table2', 'time')")
```