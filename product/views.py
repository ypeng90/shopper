from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from product.product import Product
from loguru import logger
import json
import jwt

logger.add("logs/default.log")


def get_userid(request):
    userid = 0
    token = request.session.get("jwt_token")
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        pass
    except Exception:
        logger.exception(f"jwt.decode({token}, settings.SECRET_KEY, algorithms='HS256').")
    else:
        userid = decoded.get("userid")
    return userid


def show_home(request):
    userid = get_userid(request)
    if userid:
        Product.preload(userid)
        return render(request, 'product/index.html')
    return redirect("/account/")


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


def list_all_inventory(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "stores": [], "message": "Not authenticated."})

    zipcode = json.loads(request.body).get("zipcode").strip()
    if not zipcode.strip().isdigit() or len(zipcode) != 5:
        return JsonResponse({"authenticated": True, "stores": [], "message": "Invalid zipcode."})

    msg = ""
    info = Product.list_all_inventory(userid, zipcode)
    if info is None:
        msg = "Server error."
        info = []
    return JsonResponse({"authenticated": True, "stores": info, "message": msg})
