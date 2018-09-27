from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from authentication_service.request_client import views


urlpatterns = [
    url(r"^request-form/$", login_required(views.RequestCientView.as_view()), name="request-form")
]
