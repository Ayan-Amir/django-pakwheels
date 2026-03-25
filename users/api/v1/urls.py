from django.urls import path
from users.api_views import (
    ChangePasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    ProfilePictureAPIView,
    SignupAPIView,
)

urlpatterns = [
    path('auth/signup/', SignupAPIView.as_view(), name='api_signup'),
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('users/me/', MeAPIView.as_view(), name='api_me'),
    path('users/me/change-password/', ChangePasswordAPIView.as_view(), name='api_change_password'),
    path('users/me/profile-picture/', ProfilePictureAPIView.as_view(), name='api_profile_picture'),
]
