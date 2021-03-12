# Start a TimescaleDB instance

```sh
docker run -d --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=password timescale/timescaledb:latest-pg12
docker exec -it timescaledb psql -U postgres
```

# Getting Started

```sql
-- connect to PostgreSQL 'docker exec -it timescaledb psql -U postgres'

-- create the database
CREATE database tutorial;

-- conntect to the database
\c tutorial

-- extend the database with TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- connect to the database 'docker exec -it timescaledb psql -U postgres -d tutorial'
```

## Creating a (Hyper)table

```sql
-- connect to PostgreSQL 'docker exec -it timescaledb psql -U postgres -d tutorial'

-- create a regular table
CREATE TABLE conditions (
	time TIMESTAMPTZ NOT NULL,
	location TEXT NOT NULL,
	temperature DOUBLE PRECISION NULL,
	humidity DOUBLE PRECISION NULL,
);

-- create a hypertable that is partitioned by time (using the values in the `time` column)
SELECT create_hypertable('conditions', 'time');
```

## Inserting & Querying

```sql
-- connect to PostgreSQL 'docker exec -it timescaledb psql -U postgres -d tutorial'

INSERT INTO conditions (time, location, temperature, humidity)
	VALUES (NOW(), 'office', 70.0, 50.0);

SELECT * FROM conditions ORDER BY time DESC LIMIT 100;
```

```sql
DELETE FROM conditions WHERE time < NOW() - INTERVAL '1 month';
```


## Dropping existing connections (except the current one)

```sql
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '<TARGET_DB>'
AND pid <> pg_backend_pid();
```

## Listing tables in the current database

```sql
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```