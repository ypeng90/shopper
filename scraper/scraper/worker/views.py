from django.http import JsonResponse
from worker.scraper import ScraperTarget


# Create your views here.
def target_search_products(request, keyword):
    info = ScraperTarget().search_product(keyword)
    return JsonResponse({"info": info})


def target_get_stores_by_zipcode(request, zipcode):
    info = ScraperTarget().get_stores_by_zipcode(zipcode)
    return JsonResponse({"info": info})


def target_get_quantities_by_sku_zipcode(request, sku, zipcode):
    info = ScraperTarget().get_qty_by_sku_zipcode(sku, zipcode)
    return JsonResponse({"info": info})
