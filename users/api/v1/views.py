from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.decorators.http import require_POST

from users.forms import UserInfoForm, ProfileInfoForm, ProfilePictureForm, PasswordChangeForm
from users.models import Profile


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'users/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please choose a different one.')
            return render(request, 'users/signup.html')

        user = User(username=username)
        try:
            validate_password(password, user=user)
        except ValidationError as validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            return render(request, 'users/signup.html')

        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user)

        return redirect('login')

    return render(request, 'users/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'users/login.html')


@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home_view(request):
    return render(request, 'users/home.html')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    user_form = UserInfoForm(instance=request.user)
    profile_form = ProfileInfoForm(instance=profile)
    picture_form = ProfilePictureForm(instance=profile)
    password_form = PasswordChangeForm()

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'picture_form': picture_form,
        'password_form': password_form,
    })


@login_required
@require_POST
def update_profile_info_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    user_form = UserInfoForm(request.POST, instance=request.user)
    profile_form = ProfileInfoForm(request.POST, instance=profile)

    if user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, 'Your personal information has been updated.')
    else:
        for form in (user_form, profile_form):
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)

    return redirect('profile')


@login_required
@require_POST
def update_profile_picture_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    picture_form = ProfilePictureForm(request.POST, request.FILES, instance=profile)

    if picture_form.is_valid():
        picture_form.save()
        messages.success(request, 'Your profile picture has been updated.')
    else:
        for field_errors in picture_form.errors.values():
            for error in field_errors:
                messages.error(request, error)

    return redirect('profile')


@login_required
@require_POST
def remove_profile_picture_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.profile_picture:
        profile.profile_picture.delete(save=True)
        messages.success(request, 'Your profile picture has been removed.')

    return redirect('profile')


@login_required
@require_POST
def change_password_view(request):
    password_form = PasswordChangeForm(request.POST)

    if not password_form.is_valid():
        for field_errors in password_form.errors.values():
            for error in field_errors:
                messages.error(request, error)
        return redirect('profile')

    current_password = password_form.cleaned_data['current_password']
    new_password = password_form.cleaned_data['new_password']

    if not request.user.check_password(current_password):
        messages.error(request, 'Your current password is incorrect.')
        return redirect('profile')

    try:
        validate_password(new_password, user=request.user)
    except ValidationError as validation_errors:
        for error in validation_errors:
            messages.error(request, error)
        return redirect('profile')

    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)
    messages.success(request, 'Your password has been changed successfully.')

    return redirect('profile')
