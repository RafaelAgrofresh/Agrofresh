-- cat scripts/sql/info.sql | docker exec -i timescaledb psql -U postgres -d agrofresh

-- -- List tables
-- SELECT table_name, table_type
-- FROM information_schema.tables
-- WHERE table_schema = 'public'
-- ORDER BY table_name;

-- -- List tables
-- SELECT table_name, 'hyperatable' as table_type
-- FROM timescaledb_information.hypertable
-- WHERE table_schema = 'public'
-- ORDER BY table_name;

-- schema_name |table_name| associated_schema_name | associated_table_prefix | num_dimensions | chunk_sizing_func_schema | chunk_sizing_func_name | chunk_target_size | compressed | compressed_hypertable_id
-- SELECT table_name
-- FROM _timescaledb_catalog.hypertable
-- WHERE schema_name = 'public'
-- ORDER BY table_name;


--select * from hypertable_relation_size('historical_booleanmeasurementdata')
-- --table_bytes | index_bytes | toast_bytes | total_bytes

-- select
--     t.table_name as tname,
--     not h.table_name is null as is_hypertable
-- from information_schema.tables as t
-- left join timescaledb_information.hypertable as h
-- on h.table_name = t.table_name

-- https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADMIN-DBSIZE

select r.table_name, r.is_hypertable,
    r.table_size, r.index_size, r.total_size,
    (r.total_size::float / pg_database_size(current_catalog)  * 100) as tpc
from (
    select t.table_name,
        not h.table_name is null as is_hypertable,
        GREATEST(
            pg_table_size(quote_ident(t.table_name)), -- includes TOAST
            (select coalesce(table_bytes, 0) + coalesce(toast_bytes, 0)
                from hypertable_relation_size(quote_ident(h.table_name)))
        ) as table_size,
        GREATEST(
            pg_indexes_size(quote_ident(t.table_name)),
            (select coalesce(index_bytes, 0)
                from hypertable_relation_size(quote_ident(h.table_name)))
        ) as index_size,
        GREATEST(
            pg_total_relation_size(quote_ident(t.table_name)),
            (select coalesce(total_bytes, 0)
                from hypertable_relation_size(quote_ident(h.table_name)))
        )  as total_size
    from information_schema.tables as t
    left join timescaledb_information.hypertable as h
    on h.table_name = t.table_name
    where t.table_schema = 'public'
      and t.table_type like '%TABLE%') as r
order by 4 desc, 3 desc, 2 desc