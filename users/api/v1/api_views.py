from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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
    ProfilePictureSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken


class SignupAPIView(APIView):
    """Create a new user + empty profile."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {'detail': 'Account created.', 'username': user.username},
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    """Check password and attach the user to the session (same as template login)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return Response(
                {'detail': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        # Generate JWT Tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'accessToken': str(refresh.access_token),
            'username': user.username,
            'detail': 'Logged in successfully.'
        })


class LogoutAPIView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"detail": "Invalid or missing refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserRetrieveUpdateAPIView(APIView):
    """Return or update the current user + profile (no generic class — one method per HTTP verb)."""

    def get(self, request):
        Profile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        Profile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        Profile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordAPIView(APIView):
    """Verify current password, then set a new one (keeps session logged in)."""

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context = {'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user

        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        
        update_session_auth_hash(request, user)
        
        return Response({'detail': 'Password changed successfully.'})


class ProfilePictureUpdateDestroyAPIView(APIView):
    """Upload (PATCH) or remove (DELETE) the profile image."""

    def patch(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        
        serializer = ProfilePictureSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        url = request.build_absolute_uri(profile.profile_picture.url)
        return Response({'profile_picture': url})

    def delete(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.profile_picture:
            profile.profile_picture.delete(save=True)
            profile.profile_picture = None
            profile.save(update_fields=['profile_picture'])
        return Response(status=status.HTTP_204_NO_CONTENT)
