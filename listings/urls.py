from django.urls import path
from . import views

urlpatterns = [
    path("add-product/", views.add_product, name="add_product"),
    path("product-list/", views.product_list, name="product_list"),
    path('product-detail/<int:id>/', views.product_detail, name="product_detail"),
]
