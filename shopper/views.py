from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from shopper.scraper import ScraperTarget
from shopper.shopper import Shopper
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
        return render(request, 'shopper/index.html')
    return redirect("account/login/")


def search_product(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "product": dict()})

    data = json.loads(request.body)
    store, keyword = data.get("store").strip(), data.get("keyword").strip()
    info = dict()
    if store == "tgt":
        info = ScraperTarget().search_product(keyword)
        if info is None:
            info = dict()
            message = "Invalid input."
        elif not info:
            message = "Not found."
        else:
            message = "Found."
    return JsonResponse({"authenticated": True, "product": info, "message": message})


def add_product(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "message": "Not authenticated."})

    data = json.loads(request.body)
    store, product = data.get("store"), data.get("product")
    sku, name = product.get("sku"), product.get("name").strip()
    result = Shopper.add_product(userid, sku, name, store)
    if result is None:
        message = "Internal server error."
    elif result:
        message = "Product has been added."
    else:
        message = "Failed to add product."
    return JsonResponse({"authenticated": True, "message": message})


def list_all_products(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "products": []})

    info = Shopper.list_all_products(userid)
    if info is None:
        print("Server Error")
        info = []
    return JsonResponse({"authenticated": True, "products": info})


def update_product(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "message": "Not authenticated."})

    data = json.loads(request.body).get("product")
    sku, store, track = data.get("sku"), data.get("store").lower(), int(data.get("track"))
    result = Shopper.update_product(userid, sku, store, track)
    if result is None:
        message = "Internal server error."
    elif result:
        message = "Product has been updated."
    else:
        message = "Failed to update product."
    return JsonResponse({"authenticated": True, "message": message})


def list_all_inventory(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "stores": []})

    zipcode = json.loads(request.body).get("zipcode").strip()
    if not zipcode.strip().isdigit() or len(zipcode) != 5:
        print("Invalid Input")
        return JsonResponse({"authenticated": True, "stores": []})

    Shopper.delete_all_inventory(userid)
    products = Shopper.list_all_products(userid, track=True)
    for product in products:
        sku = product.get("sku")
        store = product.get("store")
        if store == "tgt":
            ScraperTarget().get_qty_by_sku_zipcode(userid, sku, zipcode)

    info = Shopper.list_all_inventory(userid, zipcode)
    if info is None:
        print("Server Error")
        info = []
    return JsonResponse({"authenticated": True, "stores": info})
