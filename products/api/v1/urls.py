from django.urls import path
from products.api.v1.api_views import (
    CategoryDetailAPIView,
    CategoryListAPIView,
    ProductDetailAPIView,
    ProductFavoriteAPIView,
    ProductListCreateAPIView,
    ProductReviewAPIView,
    GlobalStatsHistoryAPIView,
    GlobalStatsLatestAPIView,
    GlobalStatsAPIView,
)

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='categories'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category_detail'),
    path('', ProductListCreateAPIView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail'),
    path('<int:pk>/favorite/', ProductFavoriteAPIView.as_view(), name='product_favorite'),
    path('<int:pk>/reviews/', ProductReviewAPIView.as_view(), name='product_reviews'),
    path('statistics/global/', GlobalStatsAPIView.as_view(), name='global_statistics'),
    path('statistics/global/latest/', GlobalStatsLatestAPIView.as_view(), name='global_statistics_latest'),
    path('statistics/global/history/', GlobalStatsHistoryAPIView.as_view(), name='global_statistics_history'),
]
