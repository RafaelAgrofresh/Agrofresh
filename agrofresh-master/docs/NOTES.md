# [Django Dashboard CoreUI](https://appseed.us/admin-dashboards/django-dashboard-coreui)

> **Open-Source Admin Dashboard** coded in **Django Framework** by **AppSeed** [Web App Generator](https://appseed.us/app-generator) - Features:

- Base UI Kit: **CoreUI Dashboard** (Free Version) provided by **CoreUI** agency
- Jinja2 Theme: [Jinja2 Theme - CoreUI (Free Version)](https://github.com/app-generator/theme-jinja2-coreui)
- UI-Ready app, SQLite Database, Django Native ORM
- Modular design, clean code-base
- Session-Based Authentication, Forms validation
- Deployment scripts: Docker, Gunicorn / Nginx
- **[MIT License](https://github.com/app-generator/license-mit)**
- Free support via **Github** issues tracker
- Paid 24/7 Live Support via [Discord](https://discord.gg/fZC6hup).

> Links

- [Django Dashboard CoreUI](https://django-dashboard-coreui.appseed.us/) - LIVE Demo
- [Django Dashboard CoreUI](https://appseed.us/admin-dashboards/django-dashboard-coreui) - Official product page
- More [Django Admin Dashboards](https://appseed.us/admin-dashboards/django) - index hosted by **[AppSeed](https://appseed.us)**
- [Open-Source Admin Dashboards](https://appseed.us/admin-dashboards/open-source) - index hosted by **[AppSeed](https://appseed.us)**

<br />

![Django Dashboard CoreUI - Template project provided by AppSeed.](https://raw.githubusercontent.com/app-generator/django-dashboard-coreui/master/media/django-dashboard-coreui-screen.png)

<br />

## How to use it

```sh
$ # Get the code
$ git clone https://github.com/app-generator/django-dashboard-coreui.git
$ cd django-dashboard-coreui
$
$ # Virtualenv modules installation (Unix based systems)
$ virtualenv env
$ source env/bin/activate
$
$ # Virtualenv modules installation (Windows based systems)
$ # virtualenv env
$ # .\env\Scripts\activate
$
$ # Install modules - SQLite Storage
$ pip3 install -r requirements.txt
$
$ # Create tables
$ python manage.py makemigrations
$ python manage.py migrate
$
$ # Start the application (development mode)
$ python manage.py runserver # default port 8000
$
$ # Start the app - custom port
$ # python manage.py runserver 0.0.0.0:<your_port>
$
$ # Access the web app in browser: http://127.0.0.1:8000/
```

> Note: To use the app, please access the registration page and create a new user. After authentication, the app will unlock the private pages.

<br />

## Code-base structure

The project is coded using a simple and intuitive structure presented bellow:

```sh
< PROJECT ROOT >
   |
   |-- core/                               # Implements app logic and serve the static assets
   |    |-- settings.py                    # Django app bootstrapper
   |    |-- wsgi.py                        # Start the app in production
   |    |-- urls.py                        # Define URLs served by all apps/nodes
   |    |
   |    |-- static/
   |    |    |-- <css, JS, images>         # CSS files, Javascripts files
   |    |
   |    |-- templates/                     # Templates used to render pages
   |         |
   |         |-- includes/                 # HTML chunks and components
   |         |    |-- navigation.html      # Top menu component
   |         |    |-- sidebar.html         # Sidebar component
   |         |    |-- footer.html          # App Footer
   |         |    |-- scripts.html         # Scripts common to all pages
   |         |
   |         |-- layouts/                  # Master pages
   |         |    |-- base-fullscreen.html # Used by Authentication pages
   |         |    |-- base.html            # Used by common pages
   |         |
   |         |-- accounts/                 # Authentication pages
   |         |    |-- login.html           # Login page
   |         |    |-- register.html        # Register page
   |         |
   |      index.html                       # The default page
   |     page-404.html                     # Error 404 page
   |     page-500.html                     # Error 404 page
   |       *.html                          # All other HTML pages
   |
   |-- authentication/                     # Handles auth routes (login and register)
   |    |
   |    |-- urls.py                        # Define authentication routes
   |    |-- views.py                       # Handles login and registration
   |    |-- forms.py                       # Define auth forms
   |
   |-- app/                                # A simple app that serve HTML files
   |    |
   |    |-- views.py                       # Serve HTML pages for authenticated users
   |    |-- urls.py                        # Define some super simple routes
   |
   |-- requirements.txt                    # Development modules - SQLite storage
   |
   |-- .env                                # Inject Configuration via Environment
   |-- manage.py                           # Start the app - Django default start script
   |
   |-- ************************************************************************
```

<br />

> The bootstrap flow

- Django bootstrapper `manage.py` uses `core/settings.py` as the main configuration file
- `core/settings.py` loads the app magic from `.env` file
- Redirect the guest users to Login page
- Unlock the pages served by *app* node for authenticated users

<br />

## Deployment

The app is provided with a basic configuration to be executed in [Docker](https://www.docker.com/), [Gunicorn](https://gunicorn.org/), and [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/).

### [Docker](https://www.docker.com/) execution
---

The application can be easily executed in a docker container. The steps:

> Get the code

```sh
$ git clone https://github.com/app-generator/django-dashboard-coreui.git
$ cd django-dashboard-coreui
```

> Start the app in Docker

```sh
$ sudo docker-compose pull && sudo docker-compose build && sudo docker-compose up -d
```

> Visit `http://localhost:5005` in your browser. The app should be up & running.

<br />

### [Uvicorn](https://www.uvicorn.org/)
---

Uvicorn is a Python ASGI HTTP Server built on uvloop and httptools.

> Install using pip

```sh
$ pip install uvicorn
```
> Start the app using uvicorn binary

```sh
$ uvicorn --host=0.0.0.0 --port=8001 core.asgi:application
...
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
...
```

Visit `http://localhost:8001` in your browser. The app should be up & running.


## Credits & Links
- [Django](https://www.djangoproject.com/) - The official website
- [Boilerplate Code](https://appseed.us/boilerplate-code) - Index provided by **AppSeed**
- [Boilerplate Code](https://github.com/app-generator/boilerplate-code) - Index published on Github


## Notes
### Run server
```sh
python manage.py runserver
```

### Create superuser
```sh
python manage.py createsuperuser
```

### Creating model class
add model class in `models.py`

### Adding models classes to admin panel (admin.py)
```py
#import class
from app.models import ModelName

# register class
admin.site.register(ModelName)
```

### Adding or modifing model classes
> make migrations to database
   ```sh
   python manage.py makemigrations
   ```
> create migrations
   ```sh
   python manage.py sqlmigrate app 0001
   ```

> execute migrations
   ```sh
   python manage.py migrate
   ```

### Adding or modifing locale files (for Localization)
> make messages from code to locale file (example: en_EN for english language)
   ```sh
   # django-admin makemessages -l en
   django-admin makemessages -l en -i env -i structs_new.py --no-location
   django-admin makemessages -l es -i env -i structs_new.py --no-location
   ```
> compile locale files (excluding environment)
   ```sh
   django-admin compilemessages --ignore env
   ```

### Setting permissions and authentication
- Official: https://docs.djangoproject.com/en/3.1/topics/auth/default/
> add permissions tuples (id, description to show) on models class meta of each model
   ```sh
   class meta:
      permissions= (("can_view_params", "View Parameters"),)
   ```
> check permissions on views as attribute
   ```sh
   @permission_required('mainapp.can_view_params')
   ```
> check permissions in code
   ```sh
   if request.user.is_authenticated:
    # Do something for authenticated users.
      ...
   else:
    # Do something for anonymous users.
      ...
   ```
> create migrations
   ```sh
   python manage.py makemigrations
   ```
> execute migrations
   ```sh
   python manage.py migrate
   ```

---
[Django Dashboard CoreUI](https://appseed.us/admin-dashboards/django-dashboard-coreui) - Provided by **AppSeed** [Web App Generator](https://appseed.us/app-generator).
