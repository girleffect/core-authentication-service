FROM praekeltfoundation/python-base:3.6

ARG EXTRA_DEPS

ENV DJANGO_SETTINGS_MODULE=project.settings

# Git is required because one of the pip requirements is pulled from github.
RUN apt-get update && apt-get install -y git gcc netcat $EXTRA_DEPS gettext libgettextpo-dev

RUN mkdir /static

WORKDIR /app/

COPY ./requirements /app/requirements

RUN pip3 install --no-cache-dir -r /app/requirements/requirements.txt --src /usr/local/src

COPY . /app/

RUN ALLOWED_API_KEYS="unused" USER_DATA_STORE_API="unused" USER_DATA_STORE_API_KEY="unused" ACCESS_CONTROL_API="unused" ACCESS_CONTROL_API_KEY="unused" EMAIL_HOST_USER="unused" EMAIL_HOST_PASSWORD="unused" python manage.py compilemessages

EXPOSE 8000
