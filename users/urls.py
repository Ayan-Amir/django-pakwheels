from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update-info/', views.update_profile_info_view, name='update_profile_info'),
    path('profile/update-picture/', views.update_profile_picture_view, name='update_profile_picture'),
    path('profile/remove-picture/', views.remove_profile_picture_view, name='remove_profile_picture'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
]
