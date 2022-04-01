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

    result = ScraperTarget.list_all_products(userid)
    if result is None:
        print("Server Error")
        return JsonResponse({"authenticated": True, "products": []})

    info = []
    for sku, name, store, track in result:
        info.append({"sku": sku,
                     "name": name,
                     "store": store.upper(),
                     "track": track})
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


# def show_summary(request):
#     data = utils.get_store_summary()
#     return JsonResponse({'summary': json.loads(data) if data else []})
#
#
# def show_detail(request):
#     data = json.loads(request.body)
#     store, location_id = data.get('store'), data.get('location_id')
#     return JsonResponse({'detail': utils.get_store_detail(store, location_id)})


# def set_product(request):
#     data = json.loads(request.body)
#     store, location_id, sku = data.get('store'), data.get('location_id'), data.get('sku')
#     price, track, display = round(Decimal(data.get('price')), 2), int(data.get('track')), int(data.get('display'))
#     offset, note = int(data.get('offset')), data.get('note')
#     messages = []
#     p = models.Products.objects.filter(sku=sku, store=store)
#     if price != p[0].price:
#         p.update(price=price)
#         messages.append(f'Price has been updated for {sku}.')
#     if track != p[0].track:
#         # No use to run utils.get_single_quantity_from_website(store, sku) here because
#         # sku with track=0 in the beginning doesn't show in the form to get updated at all.
#         p.update(track=track)
#         messages.append(f'Track has been updated for {sku}.')
#     if display != p[0].display:
#         p.update(display=display)
#         messages.append(f'Display has been updated for {sku}.')
#     extras = models.Extras.objects.filter(sku=sku, store=store, location_id=location_id)
#     if (not extras and offset) or (extras and offset != extras[0].offset):
#         if not extras:
#             models.Extras.objects.create(sku=sku, store=store, location_id=location_id, offset=offset)
#         else:
#             extras.update(offset=offset)
#         messages.append(f'Offset has been updated for {sku} at {location_id}.')
#     if (not extras and note) or (extras and note != extras[0].note):
#         if not extras:
#             models.Extras.objects.create(sku=sku, store=store, location_id=location_id, note=note)
#         else:
#             extras.update(note=note)
#         messages.append(f'Note has been updated for {sku} at {location_id}.')
#     return JsonResponse({'messages': messages})


