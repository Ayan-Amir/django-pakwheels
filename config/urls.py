from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from products.api_views import (
    CategoryDetailAPIView,
    CategoryListAPIView,
    ProductDetailAPIView,
    ProductFavoriteAPIView,
    ProductListCreateAPIView,
    ProductReviewAPIView,
)
from users.api_views import (
    ChangePasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    ProfilePictureAPIView,
    SignupAPIView,
)

api_urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='api_category_list'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='api_category_detail'),
    path('products/', ProductListCreateAPIView.as_view(), name='api_product_list'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('products/<int:pk>/favorite/', ProductFavoriteAPIView.as_view(), name='api_product_favorite'),
    path('products/<int:pk>/reviews/', ProductReviewAPIView.as_view(), name='api_product_reviews'),
    path('auth/signup/', SignupAPIView.as_view(), name='api_signup'),
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('users/me/', MeAPIView.as_view(), name='api_me'),
    path('users/me/change-password/', ChangePasswordAPIView.as_view(), name='api_change_password'),
    path('users/me/profile-picture/', ProfilePictureAPIView.as_view(), name='api_profile_picture'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
    path('users/', include('users.urls')),
    path('products/', include('products.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
