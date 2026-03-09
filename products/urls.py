from django.urls import path
from . import views

urlpatterns = [
    path("add-product/", views.add_product, name="add_product"),
    path("product-list/", views.product_list, name="product_list"),
    path('product-detail/<int:id>/', views.product_detail, name="product_detail"),
    path('favorite/<int:product_id>/', views.toggle_favorite, name="toggle_favorite"),
    path("review/<int:product_id>/", views.add_review, name="add_review"),
]
