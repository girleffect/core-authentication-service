FROM praekeltfoundation/python-base:3.6

ARG EXTRA_DEPS

ENV DJANGO_SETTINGS_MODULE=project.settings

# Git is required because one of the pip requirements is pulled from github.
RUN apt-get update && apt-get install -y git

RUN apt-get update && apt-get install -y gcc netcat $EXTRA_DEPS

WORKDIR /app/

COPY ./requirements /app/requirements

RUN pip3 install --no-cache-dir -r /app/requirements/requirements.txt --src /usr/local/src

COPY . /app/

EXPOSE 8000

ENTRYPOINT ["scripts/waitFor.sh"]

CMD ["scripts/startDjango.sh"]
