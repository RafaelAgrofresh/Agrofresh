# -- Restore database backup
# https://www.postgresql.org/docs/9.4/backup-dump.html
# https://docs.timescale.com/latest/using-timescaledb/backup#pg_dump-pg_restore

pushd $(pwd)
BACKUP_FILE=`ls -t agrofresh.*.db.backup | head -n 1`

SQL="
-- Dropping existing connections (except the current one)
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'agrofresh'
AND pid <> pg_backend_pid();

-- Drop database
DROP DATABASE agrofresh;

-- Create database
CREATE DATABASE agrofresh;

\c agrofresh
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
SELECT timescaledb_pre_restore();

\! pg_restore -Fc -U postgres -d agrofresh /$BACKUP_FILE
\! rm /$BACKUP_FILE

\c agrofresh
SELECT timescaledb_post_restore();
"

docker cp $BACKUP_FILE timescaledb:/ \
&& echo "$SQL" | docker exec -i timescaledb psql -U postgres
popd
