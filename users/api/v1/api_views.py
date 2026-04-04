from django.contrib.auth import update_session_auth_hash
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Profile
from users.api.v1.serializers import (
    LoginSerializer,
    ChangePasswordSerializer,
    SignupSerializer,
    UserProfileSerializer,
    ProfilePictureSerializer,
    LogoutSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics


class SignupAPIView(generics.CreateAPIView):
    """
    Create a new user + empty profile.
    Automatically handles the POST request, validation, and saving.
    """
    
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            'detail': 'Account created.',
            'username': response.data.get('username'),
        }
        return response
    


class LoginAPIView(APIView):
    """Check password and attach the user to the session (same as template login)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT Tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'accessToken': str(refresh.access_token),
            'username': user.username,
            'detail': 'Logged in successfully.'
        })


class LogoutAPIView(APIView):
    """
    Blacklists the provided refresh token to log out the user.
    """
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Handles GET (retrieve), PUT (update), and PATCH (partial_update) 
    automatically for the logged-in user.
    """
    
    serializer_class = UserProfileSerializer

    def get_object(self):
        """
        This method tells the view: 'Don't look for an ID in the URL, 
        just use the person who is currently logged in.'
        """
        Profile.objects.get_or_create(user=self.request.user)
        return self.request.user


class ChangePasswordAPIView(generics.UpdateAPIView):
    """
    Generic-style view to update the user's password.
    """
    
    serializer_class = ChangePasswordSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        update_session_auth_hash(request, user)
        
        return Response(
            {'detail': 'Password changed successfully.'},
            status=status.HTTP_200_OK
        )
        

class ProfilePictureUpdateDestroyAPIView(generics.UpdateAPIView):
    """
    Upload (PATCH) or remove (DELETE) the profile image using generics.
    """
    
    serializer_class = ProfilePictureSerializer

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    
    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        
        profile = self.get_object()
        if profile.profile_picture:
            url = request.build_absolute_uri(profile.profile_picture.url)
            response.data = {'profile_picture': url}
        return response
    
    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.profile_picture:
            profile.profile_picture.delete(save=False)
            profile.profile_picture = None
            profile.save(update_fields=['profile_picture'])
        return Response(status=status.HTTP_204_NO_CONTENT)
