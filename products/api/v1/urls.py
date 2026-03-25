from django.urls import path
from products.api.v1.api_views import (
    CategoryDetailAPIView,
    CategoryListAPIView,
    ProductDetailAPIView,
    ProductFavoriteAPIView,
    ProductListCreateAPIView,
    ProductReviewAPIView,
)

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='api_category_list'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='api_category_detail'),
    path('products/', ProductListCreateAPIView.as_view(), name='api_product_list'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('products/<int:pk>/favorite/', ProductFavoriteAPIView.as_view(), name='api_product_favorite'),
    path('products/<int:pk>/reviews/', ProductReviewAPIView.as_view(), name='api_product_reviews'),
]
