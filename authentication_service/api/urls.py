"""
Do not modify this file. It is generated from the Swagger specification.

Routing module.
"""
from django.conf.urls import url
from django.conf import settings
from django.views.static import serve
import authentication_service.api.views as views

urlpatterns = [
    url(r"^users/(?P<user_id>.+)$", views.UsersUserId.as_view()),
    url(r"^users$", views.Users.as_view()),
    url(r"^clients/(?P<client_id>.+)$", views.ClientsClientId.as_view()),
    url(r"^clients$", views.Clients.as_view()),
]

if settings.DEBUG:
    urlpatterns.extend([
        url(r"^the_specification/$", views.__SWAGGER_SPEC__.as_view()),
        url(r"^ui/(?P<path>.*)$", serve, {"document_root": "ui",
                                          "show_indexes": True})
    ])