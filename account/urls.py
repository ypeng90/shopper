from django.urls import path
from account import views


app_name = 'account'

urlpatterns = [
    path("", views.show_home),
    path("api/captcha/", views.get_captcha),
    path("api/login/", views.login),
    path("api/register/", views.register),
]
