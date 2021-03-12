cat scripts/sql/recreate.sql | docker exec -i timescaledb psql -U postgres \
&& python manage.py migrate \
&& python manage.py loaddata users \
&& python manage.py loaddata sample_3_cold_rooms \
&& python manage.py initsuperuser
# && python manage.py createsuperuser

cat scripts/sql/sample_data.sql | docker exec -i timescaledb psql -U agrofresh

# loaddata command from local file docker container
# cat <<fixture_name.json>> | docker exec -i <<container_name_or_id>> python manage.py loaddata --format=json -