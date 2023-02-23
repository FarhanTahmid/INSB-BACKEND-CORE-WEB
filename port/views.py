from django.shortcuts import render,redirect
import datetime


# Create your views here.
def homepage(request):
    #check if user is already logged in
    user=request.user
    if (user.is_authenticated):
        return redirect('users:dashboard')
    else:
        return render(request,'port/landing_page.html')