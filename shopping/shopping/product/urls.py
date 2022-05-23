from django.urls import path
from product import views


app_name = "product"

urlpatterns = [
    path("", views.show_home),
    path("api/search_product/", views.search_product),
    path("api/add_product/", views.add_product),
    path("api/list_all/", views.list_all_products),
    path("api/update_product/", views.update_product),
    path("api/get_zipcode/", views.get_zipcode),
    path("api/list_inventory/", views.list_all_inventory),
    path("<str:jwt_token>/", views.show_home),
]
