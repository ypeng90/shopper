from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from product.product import Product
from loguru import logger
import json
import jwt
import os

logger.add("logs/default.log")


def get_userid(request, jwt_token=""):
    userid = 0
    token = jwt_token or request.session.get("jwt_token")
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError) as e:
        pass
    except Exception:
        logger.exception(f"jwt.decode({token}, settings.SECRET_KEY, algorithms='HS256').")
    else:
        userid = decoded.get("userid")
        authenticated = decoded.get("authenticated")
        if authenticated and isinstance(userid, int) and len(str(userid)) == 8:
            if jwt_token:
                request.session["jwt_token"] = jwt_token
        else:
            userid = 0
    return userid


def show_home(request, jwt_token=""):
    userid = get_userid(request, jwt_token)
    if userid:
        if jwt_token:
            return redirect("/shopping/")
        else:
            Product.preload(userid)
            return render(request, "product/index.html")
    account_host = os.environ.get("ACCOUNT_HOST")
    shopping_host = os.environ.get("SHOPPING_HOST")
    return redirect(f"http://{account_host}/account/{shopping_host}-shopping/")


def list_all_products(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "products": [], "message": "Not authenticated."})

    msg = ""
    info = Product.list_all_products(userid)
    if info is None:
        msg = "Server error."
        info = []
    return JsonResponse({"authenticated": True, "products": info, "message": msg})


def update_product(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "message": "Not authenticated."})

    data = json.loads(request.body).get("product")
    sku, store, track = data.get("sku"), data.get("store").lower(), int(data.get("track"))
    result = Product.update_product(userid, sku, store, track)
    if result is None:
        msg = "Server error."
    elif result:
        msg = "Update succeeded."
    else:
        msg = "Update failed."
    return JsonResponse({"authenticated": True, "message": msg})


def search_product(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "product": dict(), "message": "Not authenticated."})

    data = json.loads(request.body)
    store, keyword = data.get("store").strip(), data.get("keyword").strip()
    info = Product.search_product(store, keyword)
    if info is None:
        info = dict()
        msg = "Invalid input."
    elif info:
        msg = ""
    else:
        msg = "Not found."
    return JsonResponse({"authenticated": True, "product": info, "message": msg})


def add_product(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "message": "Not authenticated."})

    data = json.loads(request.body)
    store, product = data.get("store"), data.get("product")
    sku, name = product.get("sku"), product.get("name").strip()
    result = Product.add_product(userid, sku, name, store)
    if result is None:
        msg = "Server error."
    elif result:
        msg = "Add succeeded."
    else:
        msg = "Add failed."
    return JsonResponse({"authenticated": True, "message": msg})


def get_zipcode(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "zipcode": "", "message": "Not authenticated."})

    zipcode = ""
    msg = ""
    info = Product.get_zipcode(userid)
    if info is None:
        msg = "Server error."
    elif info:
        zipcode = info[0][0]
    return JsonResponse({"authenticated": True, "zipcode": zipcode, "message": msg})


def list_all_inventory(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "stores": [], "message": "Not authenticated."})

    zipcode = json.loads(request.body).get("zipcode").strip()
    if not zipcode.strip().isdigit() or len(zipcode) != 5:
        return JsonResponse({"authenticated": True, "stores": [], "message": "Invalid zipcode."})
    Product.update_zipcode(userid, zipcode)

    msg = ""
    info = Product.list_all_inventory(userid, zipcode)
    if info is None:
        msg = "Server error."
        info = []
    return JsonResponse({"authenticated": True, "stores": info, "message": msg})
