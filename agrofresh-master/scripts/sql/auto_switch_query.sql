-- cat scripts/sql/auto_switch_query.sql | docker exec -i timescaledb psql -U postgres -d agrofresh

drop function if exists get_bucket_time;
create or replace function get_bucket_time (
    ts_from timestamptz,
    ts_to timestamptz,
    points integer default 500,
    sample_time interval default interval '1 sec'
)
returns interval as $bucket_time$
    declare bucket_time interval := greatest(
        (ts_to - ts_from) / (points - 1), sample_time
    );
begin
    -- Validate args
    if ts_from >= ts_to then
        raise 'Expected (ts_from: %) < (ts_to: %)', ts_from, ts_to;
    end if;

    if bucket_time < INTERVAL '0 s' then
        raise 'Expected (bucket_time: %) > 0', bucket_time;
    end if;

    if sample_time < INTERVAL '0 s' then
        raise 'Expected (sample_time: %) > 0', sample_time;
    end if;

    if bucket_time < sample_time then
        raise 'Expected (bucket_time: %) > (sample_time: %)', bucket_time, sample_time;
    end if;

    return bucket_time;
end $bucket_time$ language plpgsql;

drop function if exists downsampled_query;
create or replace function downsampled_query (
    data_src regclass,
    sample_time interval,
    ts_from timestamptz,
    ts_to timestamptz,
    points integer default 500
) returns table (
    ts timestamptz,
    cold_room_id integer,
    measurement_id integer,
    avg float, min float, max float
) as $$
    declare bucket_time interval := get_bucket_time(ts_from, ts_to, points, sample_time);
begin
    return query
    execute format('select
        time_bucket(%L::interval, d.bucket) as ts,
        d.cold_room_id, d.measurement_id,
        avg(d.value)::float, min(d.value_min)::float, max(d.value_max)::float
        from %s as d
        where d.bucket between %L::timestamptz and %L::timestamptz
        group by d.cold_room_id, d.measurement_id, ts
        order by cold_room_id, measurement_id, ts desc', bucket_time, data_src, ts_from, ts_to);
end $$ language plpgsql;

-- autoswitch based on ts_range & retention policy
-- _aggregate_1_minute  --> retention policy ts < 2 years
-- _aggregate_1_hour    --> retention policy ts < 2 years
-- _aggregate_1_day     --> retention policy ts < 2 years
-- _aggregate_30_days   --> retention policy ts < 2 years

drop function if exists downsampled_floatdata;
create or replace function downsampled_floatdata (
    ts_from timestamptz,
    ts_to timestamptz,
    points integer default 500,
    sample_time interval default interval '1 sec'
) returns table (
    ts timestamptz,
    cold_room_id integer,
    measurement_id integer,
    value float, value_min float, value_max float
) as $$
    declare bucket_time interval := get_bucket_time(ts_from, ts_to, points, sample_time);

    declare ts_now timestamptz := now();
    declare ts_delta interval  := INTERVAL '0s';

    -- auto-switch ranges
    declare max_ts_delta_1m interval  := '3 days'::interval;        -- 4320 points/metric
    declare max_ts_delta_1h interval  := '180 days'::interval;      -- 4320 points/metric
    declare max_ts_delta_1d interval  := '4320 days'::interval;     -- 4320 points/metric
    declare max_ts_delta_30d interval := '129600 days'::interval;   -- 4320 points/metric (355 years ???)

    declare rp_limit timestamptz      := ts_now - INTERVAL '2 years';
    declare data_src regclass;
begin
    -- clamp values
    ts_to := LEAST(ts_now, ts_to);
    ts_from := GREATEST(rp_limit, ts_from);
    ts_delta := ts_to - ts_from;

    if ts_delta < max_ts_delta_1m then
        raise notice 'branch 1 to:% from:% delta:%', ts_to, ts_from, ts_delta;
        data_src :=  'historical_floatdata_aggregate_1_minute';
    elsif ts_delta < max_ts_delta_1h then
        raise notice 'branch 2 to:% from:% delta:%', ts_to, ts_from, ts_delta;
        data_src :=  'historical_floatdata_aggregate_1_hour';
    elsif ts_delta < max_ts_delta_1d then
        raise notice 'branch 3 to:% from:% delta:%', ts_to, ts_from, ts_delta;
        data_src := 'historical_floatdata_aggregate_1_day';
    elsif ts_delta < max_ts_delta_30d then
        raise notice 'branch 4 to:% from:% delta:%', ts_to, ts_from, ts_delta;
        data_src := 'historical_floatdata_aggregate_30_days';
    else
        raise 'The data range is too large (ts_from: %, ts_to: %)', ts_from, ts_to;
    end if;

    return query
    select * from downsampled_query(
        data_src => data_src,
        sample_time => sample_time,
        ts_from => ts_from,
        ts_to => ts_to,
        points => points);
end $$ language plpgsql;

SELECT * FROM downsampled_floatdata(now() - INTERVAL '1d' , now()) limit 2;
SELECT * FROM downsampled_floatdata(now() - INTERVAL '10d' , now()) limit 2;
SELECT * FROM downsampled_floatdata(now() - INTERVAL '300d' , now()) limit 2;
SELECT * FROM downsampled_floatdata(now() - INTERVAL '1y 100d' , now()) limit 2;


drop function if exists downsampled_integerdata;
create or replace function downsampled_integerdata (
    ts_from timestamptz,
    ts_to timestamptz,
    points integer default 500,
    sample_time interval default interval '1 sec'
) returns table (
    ts timestamptz,
    cold_room_id integer,
    measurement_id integer,
    value float, value_min float, value_max float
) as $$
    declare bucket_time interval := get_bucket_time(ts_from, ts_to, points, sample_time);

    declare ts_now timestamptz := now();
    declare ts_delta interval  := INTERVAL '0s';

    -- auto-switch ranges
    declare max_ts_delta_1m interval  := '3 days'::interval;        -- 4320 points/metric
    declare max_ts_delta_1h interval  := '180 days'::interval;      -- 4320 points/metric
    declare max_ts_delta_1d interval  := '4320 days'::interval;     -- 4320 points/metric
    declare max_ts_delta_30d interval := '129600 days'::interval;   -- 4320 points/metric (355 years ???)

    declare rp_limit timestamptz      := ts_now - INTERVAL '2 years';
    declare data_src regclass;
begin
    -- clamp values
    ts_to := LEAST(ts_now, ts_to);
    ts_from := GREATEST(rp_limit, ts_from);
    ts_delta := ts_to - ts_from;

    if ts_delta < max_ts_delta_1m then
        raise notice 'branch 1 to:% from:% delta:%', ts_to, ts_from, ts_delta;
        data_src :=  'historical_integerdata_aggregate_1_minute';
    elsif ts_delta < max_ts_delta_1h then
        raise notice 'branch 2 to:% from:% delta:%', ts_to, ts_from, ts_delta;
        data_src :=  'historical_integerdata_aggregate_1_hour';
    elsif ts_delta < max_ts_delta_1d then
        raise notice 'branch 3 to:% from:% delta:%', ts_to, ts_from, ts_delta;
        data_src := 'historical_integerdata_aggregate_1_day';
    elsif ts_delta < max_ts_delta_30d then
        raise notice 'branch 4 to:% from:% delta:%', ts_to, ts_from, ts_delta;
        data_src := 'historical_integerdata_aggregate_30_days';
    else
        raise 'The data range is too large (ts_from: %, ts_to: %)', ts_from, ts_to;
    end if;

    return query
    select * from downsampled_query(
        data_src => data_src,
        sample_time => sample_time,
        ts_from => ts_from,
        ts_to => ts_to,
        points => points);
end $$ language plpgsql;

SELECT * FROM downsampled_integerdata(now() - INTERVAL '1d' , now()) limit 2;
SELECT * FROM downsampled_integerdata(now() - INTERVAL '10d' , now()) limit 2;
SELECT * FROM downsampled_integerdata(now() - INTERVAL '300d' , now()) limit 2;
SELECT * FROM downsampled_integerdata(now() - INTERVAL '1y 100d' , now()) limit 2;