from django.urls import path
from users.api.v1.api_views import (
    ChangePasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    ProfilePictureAPIView,
    SignupAPIView,
)

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('', MeAPIView.as_view(), name='me'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
    path('profile-picture/', ProfilePictureAPIView.as_view(), name='profile_picture'),
]
