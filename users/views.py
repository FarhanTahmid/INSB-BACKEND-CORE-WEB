from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users import registerUser
from users.ActiveUser import ActiveUser

# Create your views here.
def login(request):
    '''Logs in an user only if he is an super user'''
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(username=username,password=password)
        
        if user is not None and user.is_superuser:
            auth.login(request,user)
            
            return redirect('users:dashboard')
        else:
            messages.info(request,"Credentials given are wrong")
            return redirect('users:login')     
    else:
        return render(request,'users/login.html')
@login_required
def dashboard(request):
    if request.method=='POST':
        
        #this block of code contains codes for directly feeding info to SQL table from excel files
        if request.POST.get("feed_members"):
            registerUser.Registration.populateMembersDataThroughExcel() #feeding the sql table "MEMBERS" throuht his class
            return redirect("users:dashboard")
        else:
            print("Didnt get data from post")
            return redirect("users:dashboard")
            
    return render(request,"users/dashboard.html")