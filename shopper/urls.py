from django.urls import path
from shopper import views


app_name = "shopper"

urlpatterns = [
    path("", views.show_home),
    path("api/search_product/", views.search_product),
    path("api/add_product/", views.add_product),
    path("api/list_all/", views.list_all_products),
    path("api/update_product/", views.update_product),
]
