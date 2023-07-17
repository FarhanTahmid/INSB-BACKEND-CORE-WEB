from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users import registerUser
from django.db import connection
from django.db.utils import IntegrityError
from recruitment.models import recruited_members
from . models import Members,ResetPasswordTokenTable
import csv,datetime
from django.db import DatabaseError
from . import renderData
from django.utils.datastructures import MultiValueDictKeyError
from membership_development_team.renderData import MDT_DATA
from . import email_handler

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
    try:
        account_active_status=MDT_DATA.get_member_account_status(profile_data['ieee_id'])
    except:
        account_active_status=True
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


def forgotPassword_getUsername(request):
    '''this function is used to get the username for password resetting and sending them an email with reset link'''
    if request.method=="POST":
        getUsername=request.POST.get('username')
        
        try:
            if not User.objects.filter(username=getUsername).first():
                messages.error(request,"No user is registered with this IEEE ID")
                return redirect('users:fp_validation')
            else:
                #get the user from User Table
                getUser=User.objects.get(username=getUsername)
                #get the token sent to the user in email and check if the mail was sent
                token,mail_sent=email_handler.EmailHandler.sendForgetPasswordLinkToUserViaEmail(request,getUser.email,getUsername)
                if(mail_sent):
                    try:
                        # if the mail was sent to the user, delete all the previous tokens the user generated for password reset
                        ResetPasswordTokenTable.objects.filter(user=getUser).delete()
                    except Exception as e:
                        print(e)
                        messages.error(request,"An internal database error occured! Try again")
                    
                    #create a new row for the user with the generated to cross match later
                    new_user_request=ResetPasswordTokenTable.objects.create(user=getUser,token=token)
                    new_user_request.save()
                    messages.success(request,"An email has been sent to your email. Further intstructions for resetting your password are given there.")
                    return redirect('users:fp_validation')
                else:
                    #handles the error of if email was not send to the user.
                    messages.error(request,"Sorry, we could not process your request at this moment.")
                    return redirect('users:fp_validation')
        except Exception as e:
            print(e)
    
    
    return render(request,"users/forgot_password1.html")

def forgotPassword_resetPassword(request,username,token):
    '''Resets user password by validating the token and link'''
    
    #gets the username from link generated and user clicked from their mail.
    try:
        #searches fro user entry, used get as their will be only one instance(must) per user. if there are multiple the process wont work
        getUserTokenInfo=ResetPasswordTokenTable.objects.get(user=User.objects.get(username=username))
    except:
        return redirect('users:invalid_url')
    #validating the token by cross matching with the database
    if(getUserTokenInfo.token==token):
        if request.method=="POST":
            new_password=request.POST.get('password')
            confirm_password=request.POST.get('confirm_password')
            
            #password length must be greater than 6 characters
            if(len(new_password)>6):
                #if new and confirmed password matches:
                if(new_password==confirm_password):
                    try:
                        #changing the user password , thus resetting it
                        user=User.objects.get(username=username)
                        user.set_password(new_password)
                        user.save()
                        #deleting the used token so that it can not be used later. Thus, clicking on the same URL will show that it was invalid
                        getUserTokenInfo.delete()
                        return redirect('users:login')
                    except Exception as e:
                        print(e)
                        messages.error(request,"Password Changing Failed")
                else:
                    messages.error(request,"Two passwords did not match! Please Try again.")
            else:
                messages.error(request,"Your password must be greater than 6 characters!")
    else:
        return redirect('users:invalid_url')
    
    return render(request,"users/forgot_password2.html")

def invalidURL(request):
    '''shows the invalid URL Page'''
    return render(request,'users/invalid_url.html')