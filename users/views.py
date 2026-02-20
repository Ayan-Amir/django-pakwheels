from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'users/signup.html')

        user = User(username=username)
        try:
            validate_password(password, user=user)
        except ValidationError as validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            return render(request, 'users/signup.html')

        try:
            User.objects.create_user(username=username, password=password)
        except IntegrityError:
            messages.error(request, 'Username is already taken. Please choose a different one.')
            return render(request, 'users/signup.html')

        return redirect('login')

    return render(request, 'users/signup.html')
        

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
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
