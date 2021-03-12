-- cat scripts/sql/setup.sql | docker exec -i timescaledb psql -U postgres -d agrofresh

-- Configuration (enabled measurements)
update historical_measurement
set enabled = false;

update historical_measurement
set enabled = true
where name in ('temperatureInside', 'humidityInside', 'CO2Measure', 'C2H4Measure');

update historical_measurement
set enabled = true
where name like '%Activated';

-- Populate sample data
do $$
declare
	cold_room record;
	measurement record;
	ts_from timestamptz := now() - INTERVAL '1 year';
	ts_to   timestamptz := now();
	sample_time interval := INTERVAL '1 sec';
begin
	for cold_room in (select id from cold_rooms_coldroom) loop

		-- numeric data
		for measurement in (
			select id from historical_measurement
			where enabled = true and type = 'float'
		) loop
			raise notice 'float measurement:% @ cold_room:%', measurement.id, cold_room.id;
			INSERT INTO historical_floatdata (id, ts, value, cold_room_id, measurement_id)
			SELECT
				1 as id,
				generate_series::timestamptz as ts,
				10 * (cold_room.id + 2 * (random() - 0.5)) as value,
				cold_room.id::integer as cold_room_id,
				measurement.id::integer as measurement_id
				FROM generate_series(ts_from, ts_to, sample_time);
		end loop;

		-- boolean data
		for measurement in (
			select id from historical_measurement
			where enabled = true and type = 'bool'
		) loop
			raise notice 'bool  measurement:% @ cold_room:%', measurement.id, cold_room.id;
			with
				serie as (
					select
						generate_series as ts,
						random() > 0.5 as value
					from generate_series(ts_from, ts_to, 10 * sample_time)
				),
				serie_lag as (
					select
						ts,
						value,
						(value != lag(value) over (order by ts)) as change
					from serie
				)
				INSERT INTO historical_booleandata (id, ts, value, cold_room_id, measurement_id)
				SELECT
					1 as id,
					ts,
					value,
					cold_room.id::integer as cold_room_id,
					measurement.id::integer as measurement_id
				FROM serie_lag where change;
		end loop;
	end loop;
end; $$
