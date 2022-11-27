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
def login(request):
    '''Logs in an user only if he is an super user'''
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(username=username,password=password)
        
        if user is not None and user.is_superuser:
            auth.login(request,user)
            return redirect('users:dashboard')
        elif user is not None and User is not user.is_superuser :
            messages.info(request,"You are not allowed to login to this site")
            return redirect('users:login') 
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
        # if request.POST.get("feed_data"):
        #     print("clicked")
        #     '''This function is used to populate members in the MEMBERS table through CSV files'''
        #     with open("./DATA/Fall_2020_Recruited_Members.csv", 'r') as file_registered_members:
        #         fileReader = csv.reader(file_registered_members)
        #         for row in fileReader:
        #             if ("ï»¿" in row[0]):
        #                 continue
        #             else:
                        
        #                     addMember = recruited_members(
        #                                         nsu_id=row[0],
        #                                         first_name=row[1],
        #                                         middle_name=row[2],
        #                                         last_name=row[3],
        #                                         date_of_birth=datetime.datetime.strptime(row[4], "%m/%d/%Y").strftime("%Y-%m-%d"),
        #                                         email_personal=row[5],
        #                                         gender=row[6],
        #                                         home_address=row[7],
        #                                         major=row[8],
        #                                         graduating_year=row[9],
        #                                         session_id=row[10],
        #                                         recruited_by=row[11],
        #                                         cash_payment_status=row[12],
        #                                         ieee_payment_status=row[13]
        #                                         )
        #                     addMember.save()
                        
        else:
            return redirect("users:dashboard")
        
            
    return render(request,"users/dashboard.html") 