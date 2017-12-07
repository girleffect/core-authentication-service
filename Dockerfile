FROM praekeltfoundation/django-bootstrap

COPY authentication_service/ /app
RUN pip install -e .

ENV DJANGO_SETTINGS_MODULE authentication_service.settings
ENV CELERY_APP authentication_service

RUN django-admin collectstatic --noinput

CMD ["authentication_service.wsgi:application"]
