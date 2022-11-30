from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users import registerUser
from django.db import connection
from django.db.utils import IntegrityError
from recruitment.models import recruited_members
import csv,datetime
from users.ActiveUser import ActiveUser

# Create your views here.
def central_home(request):
    return render(request,'central_home.html')
def event_control(request):
    return render(request,'event_control_page.html')