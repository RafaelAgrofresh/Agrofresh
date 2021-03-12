# -- Create database backup
# https://www.postgresql.org/docs/9.4/backup-dump.html
# https://docs.timescale.com/latest/using-timescaledb/backup#pg_dump-pg_restore

BACKUP_FILE=$(pwd)/agrofresh.$(date +%Y-%m-%d-%H.%M.%S).db.backup # avoid fnames with ':' in docker cp
docker exec -i timescaledb pg_dump -Fc -U postgres agrofresh > $BACKUP_FILE
