from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
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
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'users/login.html')

@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):  
    return render(request, 'users/home.html')
