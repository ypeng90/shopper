from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from shopper.scraper import ScraperTarget
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
            print("invalid input")
            info = dict()
        elif not info:
            print("not found")
    return JsonResponse({"authenticated": True, "product": info})


def add_product(request):
    userid = get_userid(request)
    if userid == 0:
        return JsonResponse({"authenticated": False, "message": "Not authenticated."})

    data = json.loads(request.body)
    store, product = data.get("store"), data.get("product")
    sku, name = product.get("sku"), product.get("name").strip()
    result = ScraperTarget.add_product(userid, sku, name, store)
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

    info = ScraperTarget.list_all_products(userid)
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
    result = ScraperTarget.update_product(userid, sku, store, track)
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
    info = ScraperTarget.list_all_inventory(userid, zipcode)
    if info is None:
        print("Server Error")
        info = []
    return JsonResponse({"authenticated": True, "stores": info})
