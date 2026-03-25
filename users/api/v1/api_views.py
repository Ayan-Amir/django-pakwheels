from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Profile
from users.api.v1.serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    SignupSerializer,
    UserMeSerializer,
)


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
                status=status.HTTP_400_BAD_REQUEST,
            )
        login(request, user)
        return Response({'detail': 'Logged in.', 'username': user.username})


class LogoutAPIView(APIView):
    """Clear the session."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(APIView):
    """Return or update the current user + profile (no generic class — one method per HTTP verb)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        Profile.objects.get_or_create(user=request.user)
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        Profile.objects.get_or_create(user=request.user)
        serializer = UserMeSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        Profile.objects.get_or_create(user=request.user)
        serializer = UserMeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordAPIView(APIView):
    """Verify current password, then set a new one (keeps session logged in)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current = serializer.validated_data['current_password']
        new = serializer.validated_data['new_password']
        confirm = serializer.validated_data['confirm_password']

        if new != confirm:
            return Response(
                {'confirm_password': ['New passwords do not match.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if not user.check_password(current):
            return Response(
                {'current_password': ['Your current password is incorrect.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new, user=user)
        except ValidationError as exc:
            return Response(
                {'new_password': list(exc.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new)
        user.save()
        update_session_auth_hash(request, user)
        return Response({'detail': 'Password changed successfully.'})


class ProfilePictureAPIView(APIView):
    """Upload (PATCH) or remove (DELETE) the profile image."""

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if 'profile_picture' not in request.FILES:
            return Response(
                {'profile_picture': ['No file was submitted.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        url = request.build_absolute_uri(profile.profile_picture.url)
        return Response({'profile_picture': url})

    def delete(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.profile_picture:
            profile.profile_picture.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
