from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Fields stored on Profile (bio, phone, city, picture)."""

    class Meta:
        model = Profile
        fields = ('bio', 'phone_number', 'city', 'profile_picture')
        extra_kwargs = {'profile_picture': {'required': False}}


class UserProfileSerializer(serializers.ModelSerializer):
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


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'password')

    def validate_password(self, value):
        
        username = self.initial_data.get('username', '')
        user = User(username=username)
        
        try:
            validate_password(value, user=user)
        except ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """POST /api/auth/login/ — checks username + password are present."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid username or password.')
        
        data['user'] = user
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    def validate(self, attrs):
       self.token = attrs['refresh']
       return attrs
   
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError({"detail": "Token is invalid or expired."})
    
    
class ChangePasswordSerializer(serializers.Serializer):
    """POST /api/users/me/change-password/ — three fields; rules checked in the view."""

    current_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate_current_password(self, value):
        """
        Check if the 'current_password' entered matches the user's actual password.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Your current password is incorrect.")
        return value
    
    def validate(self, data):
        """
        Check if new passwords match and meet Django's security standards.
        """
        user = self.context['request'].user
        new_pwd = data.get('new_password')
        confirm_pwd = data.get('confirm_password')

        # 1. Match check
        if new_pwd != confirm_pwd:
            raise serializers.ValidationError({
                "confirm_password": "New passwords do not match."
            })

        try:
            validate_password(new_pwd, user=user)
        except ValidationError as e:
            raise serializers.ValidationError({
                "new_password": list(e.messages)
            })

        return data


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('profile_picture',)
        # The validations should always be handled by serializer
        extra_kwargs = {'profile_picture': {"required": True}}
