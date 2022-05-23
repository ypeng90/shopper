from django.urls import path
from authen import views


app_name = "authen"

urlpatterns = [
    path("", views.show_home),
    path("api/captcha/", views.get_captcha),
    path("api/login/", views.login),
    path("api/register/", views.register),
    path("<str:requested_host>/", views.show_home),
]
