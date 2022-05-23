"""scraper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from worker import views

urlpatterns = [
    path(
        "target/product/<str:keyword>/",
        views.target_search_products
    ),
    path(
        "target/store/<str:zipcode>/",
        views.target_get_stores_by_zipcode
    ),
    path(
        "target/quantity/<str:sku>/<str:zipcode>/",
        views.target_get_quantities_by_sku_zipcode
    ),
]
