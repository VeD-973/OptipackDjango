from django.shortcuts import render,redirect
from django.http import HttpResponse ##used for direct returning the html tags.
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from home.models import *
from django.contrib import messages
from django.db import IntegrityError
from home.decorators import custom_login_required
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def generate_unique_user_id():
    while True:
        # Generate a random six-digit number
        random_id = random.randint(100000, 999999)
        
        # Check if the random_id is unique in the Users model
        if not Users.objects.filter(user_id=random_id).exists():
            return random_id

def home(request):
    return render(request, "home.html")

def freeTrial(request):
    return render(request, 'freeTrial.html')

def joinCreateOrganisation(request):
    return render(request, 'login.html')  # Assuming this is your join/create organisation template


def additionalInformation(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        company_name = request.POST.get('company-name')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'additionalInformation.html')

        company, created = Company.objects.get_or_create(company_name=company_name)

        if created and not company.company_code:
            company.company_code = company.generate_unique_code()
            company.save()

        # Check if a user with the provided email already exists
        user_exists = Users.objects.filter(email_id=email).exists()
        if user_exists:
            messages.error(request, "An account with this email already exists.")
            return render(request, 'additionalInformation.html')

        # Create a new user
        user = Users(
            email_id=email,
            user_id=generate_unique_user_id(),
            user_first_name='DefaultFirstName',  # Replace with actual form data or defaults
            user_last_name='DefaultLastName',    # Replace with actual form data or defaults
            user_type='Company_loader',          # Replace with actual logic for user type
            user_status='Active',
            is_authenticated=True,
            company=company                      # Associate with the created or retrieved company
        )

        user.set_password(password)
        user.save()

        # Authenticate and log the user in
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the dashboard after successful login
            return redirect('dashboard')
        else:
            messages.error(request, "Authentication failed. Please try logging in again.")
            return redirect('login')  # Redirect to login if authentication fails

    return render(request, 'additionalInformation.html')  # Render additional information form for GET request

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'login.html')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            user.is_authenticated= True
            user.save()
            # next_url = request.GET.get('next', 'dashboard')  # Default to 'dashboard' if 'next' is not provided
            return redirect(dashboard)  # Use the 'next' parameter if available
        else:
            return redirect('additionalInformation')

    return render(request, 'login.html')  # Render the login template in case of GET request or errors


@custom_login_required
def dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'dashboard.html', context)

@custom_login_required
def profile(request):
    context = {
        'user': request.user,
        'utilization_range': range(70, 96,5),
        'delivery_horizon_range': range(1, 21,3),
    }
    return render(request, 'profile.html',context)

def logout_view(request):
    if request.user.is_authenticated:
        user = request.user
        # Set custom authenticated field to False
        user.is_authenticated = False
        user.save()  # Save the updated authentication status in the database
        
        logout(request)  # This will clear the session and log the user out
    return redirect(home)

@csrf_exempt
def add_container(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        length = data.get('containerLength')
        width = data.get('containerWidth')
        height = data.get('containerHeight')
        max_weight = data.get('maxWeight')

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@custom_login_required
def manageUsers(request):
    return render(request, 'manageUsers.html')