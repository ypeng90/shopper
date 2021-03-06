from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from authen.account import Register, Login
from authen.captcha import Captcha
import importlib.util
import json
from loguru import logger
import os

logger.add("logs/default.log")

spec = importlib.util.spec_from_file_location("utils",
                                              os.path.join(settings.BASE_DIR,
                                                           "account/utils.py"))
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)


def show_home(request, requested_host=""):
    if requested_host:
        requested_host = "http://" + "/".join(requested_host.split("-"))
    request.session["requested_host"] = requested_host
    return render(request, "authen/index.html")


def get_captcha(request):
    captcha_text, image_data = Captcha().generate()
    request.session["captcha"] = captcha_text
    return HttpResponse(image_data, content_type="image/png")


def register(request):
    data = json.loads(request.body)
    agreement = data.get("agreement")
    username = data.get("username")
    password_1 = data.get("password_1")
    password_2 = data.get("password_2")
    captcha = data.get("captcha")
    if agreement and username and password_1 and password_2 and captcha:
        if captcha == request.session.get("captcha"):
            if username.isalnum() and 5 < len(username) < 21:
                if password_1 == password_2:
                    if len(password_1) >= 6:
                        handle = Register(username, password_1)
                        if not handle.existing:
                            if handle.add():
                                return JsonResponse({
                                    "code": 10000,
                                    "message": "You have successfully registered. Redirecting..."
                                })
                            msg = "Registration failed due to internal error."
                        else:
                            msg = "Please choose a different username."
                    else:
                        msg = "Please choose a password with at least 6 characters."
                else:
                    msg = "Please match both passwords."
            else:
                msg = "Please choose a username containing 6 to 20 letters and digits."
        else:
            msg = "Please type in correct Captcha text."
    else:
        msg = "Please type in all required information."
    return JsonResponse({"code": 10001, "message": msg})


def login(request):
    data = json.loads(request.body)
    captcha = data.get("captcha").strip()
    if captcha == request.session.get("captcha"):
        username = data.get("username").strip()
        password = data.get("password")
        if 5 < len(username) < 21 and username == utils.StrAlnumConverter(username).value and password:
            handle = Login(username, password)
            if handle.existing:
                token = handle.jwt()
                requested_host = request.session.get("requested_host")
                return JsonResponse({
                    "code": 10000,
                    "requested_host": requested_host,
                    "token": token,
                    "message": ""
                })
            else:
                msg = "Please type in valid username and password."
        else:
            msg = "Please type in valid username and password."
    else:
        msg = "Please type in correct Captcha text."
    return JsonResponse({"code": 10001, "message": msg})
