FROM praekeltfoundation/python-base:3.6

ARG EXTRA_DEPS

ENV DJANGO_SETTINGS_MODULE=project.settings

RUN apt-get update && apt-get install -y gcc netcat $EXTRA_DEPS

RUN mkdir /static

WORKDIR /app/

COPY ./requirements /app/requirements

RUN pip install -r requirements/requirements.txt

COPY . /app/

EXPOSE 8000
