from django.contrib import admin

from authentication_service.request_client import models

admin.site.register(models.RequestedClient, admin.ModelAdmin)
