FROM praekeltfoundation/python-base:3.6

ARG EXTRA_DEPS

ENV DJANGO_SETTINGS_MODULE=project.settings

RUN apt-get update && apt-get install -y gcc $EXTRA_DEPS

WORKDIR /app/

COPY ./requirements /app/requirements

RUN pip install -r requirements/requirements.txt

COPY . /app/

RUN chmod -R +x /app/scripts/

EXPOSE 8000
