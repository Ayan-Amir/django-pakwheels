from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Fields stored on Profile (bio, phone, city, picture)."""

    class Meta:
        model = Profile
        fields = ('bio', 'phone_number', 'city', 'profile_picture')
        extra_kwargs = {'profile_picture': {'required': False}}


class UserMeSerializer(serializers.ModelSerializer):
    """Logged-in user plus nested profile (GET / PATCH / PUT /api/users/me/)."""

    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'profile')
        read_only_fields = ('id', 'username')

    def update(self, user, validated_data):
        profile_data = validated_data.pop('profile', {})

        for field, value in validated_data.items():
            setattr(user, field, value)
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        for field, value in profile_data.items():
            setattr(profile, field, value)
        profile.save()

        return user


class SignupSerializer(serializers.Serializer):
    """POST /api/auth/signup/ — username + password only."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username is already taken.')
        return value

    def validate_password(self, value):
        draft_user = User(username=self.initial_data.get('username', ''))
        try:
            validate_password(value, user=draft_user)
        except ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        Profile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """POST /api/auth/login/ — checks username + password are present."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class PasswordChangeSerializer(serializers.Serializer):
    """POST /api/users/me/change-password/ — three fields; rules checked in the view."""

    current_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
