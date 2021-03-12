# Cold Storage Management App

Django based app for cold storage management.

## Run (development)
```sh
# Create virtual envoirement
python -m venv env

# Activate virtual envoirement
. env/bin/activate     # linux
. env/Scripts/activate # windows

# Install requirements
pip install -r requirements.txt

# Additional steps
python manage.py migrate            # Create database
python manage.py createsuperuser    # Create django admin account
python manage.py compilemessages    # Compiles .po files created by makemessages to .mo
python manage.py collectstatic      # Collects the static files into STATIC_ROOT ('staticfiles/')

# Run
python manage.py runserver
```

## Run (production)

Execute the automated deployment checklist and resolve the issues (optional)
```sh
python manage.py check --deploy
```

Build the docker image
```sh
docker build -t agrofresh-app .
```

If the production and development hosts are different machines, move the image to the production machine
```sh
# In development host, export the generated image to agrofresh-app.tar.gz
docker save agrofresh-app:latest | gzip -n -9 > agrofresh-app.tar.gz

# Copy agrofresh-app.tar.gz from development to production host

# In production host, import the image
gzip -d --stdout agrofresh-app.tar.gz | docker load
```

Run the multi-container docker application
```sh
docker-compose up --detach
```
