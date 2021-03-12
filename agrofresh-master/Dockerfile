# Use an official Python runtime as a parent image
FROM python:slim
# FROM python:slim@sha256:06afab4b2ca1f6094a708a4fb2c2cbcf50238e39f50a804cf5addfac984ec68c

# Make a new directory to put our code in.
RUN mkdir /code

# Change the working directory.
# Every command after this will be run from the /code directory.
WORKDIR /code

# Upgrade pip
RUN python3 -m pip install --no-cache-dir -U pip

# Install dependencies
COPY ./requirements.txt /code/

ENV BUILD_DEPS="gcc libc6-dev libpq-dev"
RUN apt-get update \
    && apt-get install -y --no-install-recommends ${BUILD_DEPS} \
    && apt-get install -y --no-install-recommends libpq5 \
    && python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y ${BUILD_DEPS} \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Mount the application code to the image
COPY . /code/

EXPOSE 8000

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]

# Build:      docker build -t agrofresh-app .
# Run & test: docker run --env DB_HOST=172.30.144.1 -it --rm -p 8000:8000 agrofresh-app
# Export:     docker save agrofresh-app:latest | gzip -n -9 > agrofresh-app.tar.gz
# Send:       wormhole send --code-length 4 --verify agrofresh-app.tar.gz # returns <codeXYZ>
# Receive:    wormhole receive <codeXYZ>
# Import:     gzip -d --stdout agrofresh-app.tar.gz | docker load

# Split:      cat agrofresh-app.tar.gz |  split -b 25M - agrofresh-app.tar.gz.splitted.
# Join:       cat agrofresh-app.tar.gz.splitted.* > agrofresh-app.tar.gz

# Multiarch
# # https://www.docker.com/blog/multi-arch-images/
# docker buildx build --platform linux/arm/v7 -t agrofresh-app .
# docker save agrofresh-app:latest | gzip -n -9 > agrofresh-app.armv7.tar.gz
# docker buildx imagetools inspect agrofresh-app
