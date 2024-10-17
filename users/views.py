from django.shortcuts import render,redirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from central_events.google_calendar_handler import CalendarHandler
from insb_port import settings
from system_administration.models import SystemErrors, adminUsers
from task_assignation.models import Member_Task_Point
from users import registerUser
from django.db import connection
from django.db.utils import IntegrityError
from recruitment.models import recruited_members
from . models import Members,ResetPasswordTokenTable,UserSignupTokenTable
import csv,datetime
from django.utils.timezone import now
from django.db import DatabaseError
from . import renderData
from django.utils.datastructures import MultiValueDictKeyError
from membership_development_team.renderData import MDT_DATA
from . import email_handler
from port.renderData import PortData
from central_events.models import Events
from django.db.models import Q
import logging
from system_administration.system_error_handling import ErrorHandling
from datetime import datetime
import traceback
from central_branch import views as cv
from .renderData import member_login_permission,get_top_5_performers,get_top_5_teams
from task_assignation.renderData import Task_Assignation
from django.utils import timezone

logger=logging.getLogger(__name__)

# Create your views here.
def login(request):
    
    '''Logs in an user only if he is an super user'''

    try:
        
        if request.method=="POST":
            username=request.POST['username']
            password=request.POST['password']
            user=auth.authenticate(username=username,password=password)
            
            if user is not None: #Checks if user exists and if the user is superuser
                # Check for the 'next' parameter in the GET request
                next_url = request.POST.get('next')
                
                auth.login(request,user)

                if next_url:
                    # Redirect to the originally requested URL
                    return redirect(next_url)
                else:
                    return redirect('users:dashboard')
            else:
                messages.info(request,"Credentials given are wrong")
                return redirect('users:login')     
        else:
            return render(request,'users/login.html')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    
    
def signup_user_validation(request):
    if(request.method=="POST"):
        if(request.POST.get('signup')):
            ieee_id=request.POST['ieee_id']
            if(not ieee_id.isnumeric()):
                messages.info(request,"Your IEEE ID is an 8 or 9 digits number.")
                return redirect('users:signup_validation')
            
            try:
                getMember=Members.objects.get(ieee_id=ieee_id)
                # check if member is already signed in
                if User.objects.filter(username=ieee_id).exists():
                    messages.info(request,"You are already signed up! Try Logging in instead.")
                    return redirect('users:signup_validation')

                # send a email with a token in signup link
                token,mail_sent=email_handler.EmailHandler.send_email_for_signup(member=getMember,request=request)
                
                if(mail_sent):
                    try:
                        # delete previous instances of signup tokens for the particular user
                        get_instace=UserSignupTokenTable.objects.filter(user=getMember)
                        if(get_instace.exists()):
                            get_instace.delete()
                    except Exception as e:
                        messages.warning(request,"Something went wrong! Please Try again.")
                        return redirect('users:signup_validation')
                    # register a new instance of request for the user
                    new_signup_request=UserSignupTokenTable.objects.create(
                        user=getMember,token=token
                    )
                    new_signup_request.save()
                    messages.success(request,f"An email has been sent to your personal email. Your signup link is given there!")
                    return redirect('users:signup_validation')
                else:
                    messages.warning(request,f"We can not process your request at this moment! Please try again.")
                    return redirect('users:signup_validation')
                    
            except Members.DoesNotExist:
                messages.warning(request,"Looks like you are not registered in our Central database yet!")
                messages.warning(request,"If you are a member of IEEE NSU SB, please contact our Membership Development Team!")                    
                return redirect('users:signup_validation')
            
    return render(request,"users/signup_user_valid.html")
    

def signup(request,ieee_id,token):
    
    '''Signs up user. only limited to IEEENSUSB Member. Checks if the member is registered in the main database'''
    
    try:

        # check if this is a valid link used
        get_user_signup_link=UserSignupTokenTable.objects.filter(user=Members.objects.get(ieee_id=ieee_id),token=token)
        # if the signuplink object exists
        if(get_user_signup_link.exists()):
            # if the token is equal to url token
            if(get_user_signup_link[0].token==token):
                
                if request.method=="POST":
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
                                if User.objects.filter(username=ieee_id).exists():
                                    messages.info(request,"You are already signed up! Try Logging in instead.")
                                else:
                                    
                                    #creating account for the user
                                    try:
                                        user = User.objects.create_user(username=ieee_id, email=getMember.email_personal,password=password)
                                        user.save()
                                        # delete the user signup link object
                                        get_user_signup_link.delete()
                                        auth.login(request,user) #logging in user after signing up automatically
                                        return redirect('users:dashboard')
                                    except:
                                        messages.info(request,"Something went wrong! Try again")
                                    
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
            else:
                return redirect('users:invalid_url')

        else:
            return redirect('users:invalid_url')
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def dashboard(request):
    '''This function loads all the dashboard activities for the program'''
    
    
    try:

        #### LOOK into registerUser.py for manual input of data from csv. Templates are created there.
        is_eb_or_admin = renderData.is_eb_or_admin(request.user)
        #getting year list for the last 5 years event chart
        years = renderData.getEventNumberStatYear()
        #getting data for the number of events over last 5 years
        event_number_over_5_years = renderData.getEventNumberStat(request,1)
        #getting data for the daily hit count
        hit_count_per_day_in_a_month = renderData.getHitCountMonthly()
        #getting data for the recruitment stats graph
        recruitement_stat = renderData.getRecruitmentStats()
        #getting data for the circular graph on portal
        type_of_events_stat = renderData.getTypeOfEventStats(request,1)
        #getting male female active inactive numbers
        male_female_active_inactive_stats = renderData.getMaleFemaleRationAndActiveStatusStats()
        #getting montly page view for the year
        hit_count_monthly = renderData.getHitCountYearly()
        #getting visitors on main website over last 5 years
        hit_count_over_5_years = renderData.getHitCountOver5Years()
        #getting monthly members with highest task completion points
        monthly_top_members = renderData.getMonthlyTopMembers()
                
        # Get the SC & AGS
        sc_ag=PortData.get_all_sc_ag(request=request)
        #scheduler.start()
        #Loading current user data from renderData.py
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        performers = get_top_5_performers(request)
        top_teams = get_top_5_teams(request)
        if(user_data==False):

            if request.method == "POST":
                
                if request.POST.get('Logout'):
                    auth.logout(request)
                    return redirect('users:login')

            return render(request,"users/access_denied_user.html") 
        context={
            'user_data':user_data,
            'eb_member':is_eb_or_admin,
            'years':years,
            'event_number_over_5_years':event_number_over_5_years,
            'hit_count_monthly':hit_count_per_day_in_a_month[2],
            'month_name':hit_count_per_day_in_a_month[0],
            'days_of_month':hit_count_per_day_in_a_month[1],
            'recruitment_stat_key':recruitement_stat[0],
            'recruitment_stat_values':recruitement_stat[1],
            'type_of_event_stats_keys':type_of_events_stat[0],
            'type_of_event_stats_values':type_of_events_stat[1],
            'event_percentage':type_of_events_stat[2],
            'gender_active_inactive_users_labels':male_female_active_inactive_stats[0],
            'gender_active_inactive_users_data':male_female_active_inactive_stats[1],
            'gender_active_inactive_users_dic':male_female_active_inactive_stats[2],
            'current_year':hit_count_monthly[0],
            'current_year_month_name':hit_count_monthly[1],
            'hit_count_monthly_data':hit_count_monthly[2],
            'hit_count_over_5_years':hit_count_over_5_years,
            'monthly_top_3_members':monthly_top_members,
            'all_sc_ag':sc_ag,
            'media_url':settings.MEDIA_URL,
            'performers':performers,
            'top_teams':top_teams,
        }

        
        return render(request,"users/dashboard.html",context=context) 
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def getDashboardStats(request):

    try:

        if request.method=="GET":
            #First get what the api is requesting form dashboard.init.js
            info_type=request.GET.get('stat_type')
            if(info_type=="recruitment_stat"):
                recruitmentStat=renderData.getRecruitmentStats()
                return JsonResponse(recruitmentStat)
            else:
                return HttpResponseBadRequest
            
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    
@login_required
@member_login_permission
def profile_page(request):
    
    '''This function loads all the view for User profile View'''

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
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
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'active_status':account_active_status
        }
        
        return render(request,"users/profile_page.html",context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

# profile settings
@login_required
@member_login_permission
def change_password(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        if request.method=="POST":
            old_password=request.POST.get('old_password')
            new_password=request.POST.get('new_password')
            confirm_password=request.POST.get('confirm_new_password')

            user=User.objects.get(username=request.user.username)
            if user.check_password(old_password):
                #password length must be greater than 6 characters
                if(len(new_password)>6):
                    #if new and confirmed password matches:
                    if(new_password==confirm_password):
                        try:
                            #changing the user password
                            user.set_password(new_password)
                            user.save()
                            auth.logout(request)
                            
                            messages.success(request,"Password Changed Successfully! Please log in again")
                            return redirect('users:login')
                        except Exception as e:
                            print(e)
                            messages.error(request,"Password Changing Failed")
                    else:
                        messages.error(request,"Two passwords did not match! Please Try again.")
                else:
                    messages.error(request,"Your password must be greater than 6 characters!")
            else:
                messages.warning(request,"Your old password is not correct!")
            
            return redirect('users:change_password')    
            

        context={
            'user_data':user_data,
            'all_sc_ag':sc_ag,
        }


        return render(request,"users/change_password.html",context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
# update profile information
def update_information(request):

    try:

        #Get current logged in user
        current_user=renderData.LoggedinUser(request.user)
        #Get the profile details of the logged in user from database
        profile_data=current_user.getUserData()
        sc_ag=PortData.get_all_sc_ag(request=request)

        if(request.method == "POST"):
            #Update clicked
            try:
                #Check if an image file was sent in request. If yes then update the current profile pic with the new one
                if('profile_picture' in request.FILES):
                    #Get the image file
                    file=request.FILES.get('profile_picture')
                    # if(file.size>(2*1024*1024)):
                    #     messages.warning(request,"Maximum File size of 2 MB exceeded!")
                    #     return redirect('users:update_information')
                    # else:
                    change_pro_pic=current_user.change_profile_picture(file) #Calling function to change profile picture of the user
                    if(change_pro_pic==False):
                        return DatabaseError
                    else:
                        messages.info(request,"Profile Picture was changed successfully!")
            except MultiValueDictKeyError:
                messages.info(request,"Please select a file first!")

            #Check if the logged in user is admin user
            if(profile_data['is_admin_user']):
                #If yes then collect the name and email only
                name = request.POST['name']
                email = request.POST['email']

                #Call the update admin function to update admin user profile information
                if(current_user.update_admin_user_data(name=name, email=email)):
                    messages.success(request, "Profile updated successfully")
                else:
                    messages.error(request, "Something went wrong while updating profile information")
            else:
                #Not admin user
                #Collect all the details
                name = request.POST['name']
                email_personal = request.POST['email_personal']
                nsu_id = request.POST['nsu_id']
                home_address = request.POST['address']
                date_of_birth = request.POST['dob']
                gender = request.POST['gender']
                email_nsu = request.POST['email_nsu']
                email_ieee = request.POST['email_ieee']
                contact_no = request.POST['contact_no']
                major = request.POST['major']
                facebook_url = request.POST['facebook_url']
                linkedin_url = request.POST['linkedin_url']
                try:
                    blood_group = request.POST['blood_group']
                except:
                    blood_group = "None"

                if date_of_birth == '':
                    date_of_birth = None

                #Call the update user data function to update the user profile information
                if(current_user.update_user_data(name=name,
                                            nsu_id=nsu_id,
                                            home_address=home_address,
                                            date_of_birth=date_of_birth,
                                            email_personal=email_personal,
                                            gender=gender,
                                            email_nsu=email_nsu,
                                            email_ieee=email_ieee,
                                            contact_no=contact_no,
                                            major=major,
                                            facebook_url=facebook_url,
                                            linkedin_url=linkedin_url,
                                            blood_group=blood_group)):
                    messages.success(request, "Profile updated successfully")
                else:
                    messages.error(request, "Something went wrong while updating profile information")                          

            return redirect('users:update_information')

        context={
            'user_data' : profile_data,
            'all_sc_ag':sc_ag,
            'picture_max_size':4*1024*1024,
        }

        return render(request,"users/update_information.html", context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)


@login_required
@member_login_permission
def logoutUser(request):
    try:

        auth.logout(request)
        return redirect('users:login')
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def forgotPassword_getUsername(request):
    '''this function is used to get the username for password resetting and sending them an email with reset link'''
    
    try:

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
                            get_instace=ResetPasswordTokenTable.objects.filter(user=getUser)
                            if(get_instace.exists()):
                                get_instace.delete()
                        except Exception as e:
                            print(e)
                            messages.error(request,"An internal database error occured! Try again")
                        
                        #create a new row for the user with the generated to cross match later
                        new_user_request=ResetPasswordTokenTable.objects.create(user=getUser,token=token)
                        new_user_request.save()
                        messages.success(request,"An email has been sent to your personal email. Further intstructions for resetting your password are given there.")
                        return redirect('users:fp_validation')
                    else:
                        #handles the error of if email was not send to the user.
                        messages.error(request,"Sorry, we could not process your request at this moment.")
                        return redirect('users:fp_validation')
            except Exception as e:
                print(e)
        
        
        return render(request,"users/forgot_password1.html")
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def forgotPassword_resetPassword(request,username,token):
    '''Resets user password by validating the token and link'''
    
    try:
    
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
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def invalidURL(request):

    try:

        '''shows the invalid URL Page'''
        return render(request,'users/invalid_url.html')
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def my_tasks(request):

    try:
        #Get current logged in user
        user = request.user.username
        # Get the SC & AGS
        sc_ag=PortData.get_all_sc_ag(request=request)
        #scheduler.start()
        #Loading current user data from renderData.py
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        all_user_tasks = Task_Assignation.load_user_tasks(user)
        total_point = 0
        try:
            user = Members.objects.get(ieee_id = user)
            total_point = user.completed_task_points
        except:
            user = adminUsers.objects.get(username=user)

        context = {
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'all_tasks':all_user_tasks,
            'total_points':total_point,
            'user':user,
        }
        return render(request,"users/my_tasks.html",context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    