FROM praekeltfoundation/django-bootstrap:py3

ARG EXTRA_DEPS

ENV DJANGO_SETTINGS_MODULE=project.settings
ENV SKIP_MIGRATIONS=1

# Git is required because one of the pip requirements is pulled from github.
RUN apt-get update && apt-get install -y git gcc netcat $EXTRA_DEPS gettext libgettextpo-dev

RUN mkdir -p /app/static

COPY . /app/

WORKDIR /app/

RUN pip3 install --no-cache-dir -r /app/requirements/requirements.txt --src /usr/local/src
RUN pip install -e .

RUN BUILDER="true" django-admin collectstatic --noinput
RUN BUILDER="true" python manage.py compilemessages

EXPOSE 8000

CMD ["project.wsgi:application"]
