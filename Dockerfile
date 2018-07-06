FROM praekeltfoundation/django-bootstrap:py3.6

ARG EXTRA_DEPS

ENV DJANGO_SETTINGS_MODULE=project.settings

# Git is required because one of the pip requirements is pulled from github.
RUN apt-get update && apt-get install -y git gcc netcat $EXTRA_DEPS gettext libgettextpo-dev

RUN mkdir -p /app/static

WORKDIR /app/

# Copy and install requirements.txt first. If requirements did not change, the
# cached layers can be re-used, which significantly speeds up the build.
COPY ./requirements/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt --src /usr/local/src

COPY . /app/

RUN pip install -e .

RUN BUILDER="true" django-admin collectstatic --noinput
RUN BUILDER="true" python manage.py compilemessages

EXPOSE 8000

CMD ["project.wsgi:application"]
