from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users import registerUser
from django.db import connection
from django.db.utils import IntegrityError
from recruitment.models import recruited_members
from . models import Members
import csv,datetime
from django.db import DatabaseError
from . import renderData
from django.utils.datastructures import MultiValueDictKeyError
from membership_development_team.renderData import MDT_DATA


# Create your views here.
def login(request):
    
    '''Logs in an user only if he is an super user'''
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(username=username,password=password)
        
        if user is not None: #Checks if user exists and if the user is superuser
            auth.login(request,user)
            return redirect('users:dashboard')
        else:
            messages.info(request,"Credentials given are wrong")
            return redirect('users:login')     
    else:
        return render(request,'users/login.html')

def signup(request):
    
    '''Signs up user. only limited to IEEENSUSB Member. Checks if the member is registered in the main database'''
    if request.method=="POST":
        ieee_id=request.POST['ieee_id'] #here collecting the ieee account as the initiator for Login.
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        
        #checking if password equals to confirm password
        #the password length must be greater than 6.
        
        if(password==confirm_password):
            if(len(password)>6):
                
                # Now find the Registered Member against the IEEE id. Matching the IEEE ID in MEMBERS table and finding their associated email with their IEEE account
                try:
                    getMember=Members.objects.get(ieee_id=ieee_id)
                    
                    #checking if the member is already signed up
                    if User.objects.filter(email=getMember.email_personal).exists():
                        messages.info(request,"You are already signed up!")
                    else:
                        
                        #creating account for the user
                        try:
                            user = User.objects.create_user(username=ieee_id, email=getMember.email_personal,password=password)
                            user.save();
                            auth.login(request,user) #logging in user after signing up automatically
                            return redirect('users:dashboard')
                        except:
                            messages.info("Something went wrong! Try again")
                        
                except Members.DoesNotExist:
                    #If the ieee id is not found:
                    
                    messages.info(request,"Looks like you are not registered in our Central database yet!")
                    messages.info(request,"If you are a member of IEEE NSU SB, please contact our Membership Development Team!")                    
                
                except ValueError:
                    messages.info(request,"Please enter your IEEE ID as Numerical Values!")
            else:
                messages.info(request,"Your password must be greater than 6 characters!")
        else:
            messages.info(request,"Two passwords Did not match!")
        
        
        
    
    
    return render(request,'users/signup.html')

@login_required
def dashboard(request):
    '''This function loads all the dashboard activities for the program'''
    
    #### LOOK into registerUser.py for manual input of data from csv. Templates are created there.

    #Loading current user data from renderData.py
    current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file
    if(user_data==False):
        return DatabaseError
    context={
        'user_data':user_data
    }

    
    return render(request,"users/dashboard.html",context=context) 


def profile_page(request):
    
    '''This function loads all the view for User profile View'''

    current_user=renderData.LoggedinUser(request.user)
    
    profile_data=current_user.getUserData()
    #get user account active status
    account_active_status=MDT_DATA.get_member_account_status(profile_data['ieee_id'])
    
    if request.method=="POST":
        
        try:
            file=request.FILES['profile_picture']
            user=renderData.LoggedinUser(request.user)
            change_pro_pic=user.change_profile_picture(file) #Calling function to change profile picture of the user
            if(change_pro_pic==False):
                return DatabaseError
            else:
                messages.info(request,"Profile Picture was changed successfully!")
                return redirect('users:profile')
        except MultiValueDictKeyError:
            messages.info(request,"Please select a file first!")
        
            
            
    context={
        'user_data':profile_data,
        'active_status':account_active_status
    }
    
    return render(request,"users/profile_page.html",context)




@login_required
def logoutUser(request):
    auth.logout(request)
    return redirect('/users/login') 