-- cat scripts/sql/recreate.sql | docker exec -i timescaledb psql -U postgres

-- Dropping existing connections (except the current one)
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'agrofresh'
AND pid <> pg_backend_pid();

-- Drop database
DROP DATABASE agrofresh;

-- Create database
CREATE DATABASE agrofresh;
