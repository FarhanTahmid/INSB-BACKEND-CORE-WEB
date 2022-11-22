from django.shortcuts import render,redirect
from django.db import DatabaseError,IntegrityError
from django.http import HttpResponseServerError,HttpResponseBadRequest
from recruitment.models import recruitment_session,recruited_members
from . import renderData
from django.contrib.auth.decorators import login_required
from . forms import StudentForm
from . models import recruited_members
from django.contrib import messages
import datetime


# Create your views here.

@login_required
def recruitment_home(request):
    
    '''Loads all the recruitment sessions present in the database
        this can also register a recruitment session upon data entry
        this passes all the datas into the template file    
    '''
    
    numberOfSessions=renderData.Recruitment.loadSession()
    if request.method=="POST":
        session_name=request.POST["recruitment_session"]
        try:
            add_session=recruitment_session(session=session_name)
            add_session.save()
        except DatabaseError:
            return DatabaseError
    return render(request,'recruitment_home.html',numberOfSessions)

@login_required  
def recruitee(request,pk):
    
    '''This function is responsible for getting all the members registered in a particular
    recruitment session. Loads all the datas and show them
    '''
    getSession=renderData.Recruitment.getSession(session_id=pk)
    
    getRecruitedMembers=renderData.Recruitment.getRecruitedMembers(session_id=pk)
    
    context={
        'session':getSession,
        'members':getRecruitedMembers,
       }
    return render(request,'recruitees.html',context=context)


@login_required
def recruitee_details(request,nsu_id):
    """Preloads all the data of the recruitees who are registered in the particular session, here we can edit and save the data of the recruitee"""
    data=renderData.Recruitment.getRecruitedMemberDetails(nsu_id=nsu_id)
    dob=datetime.datetime.strptime(str(data['recruited_member'][0]['date_of_birth']), "%Y-%m-%d").strftime("%Y-%m-%d") #this dob does not change any internal data, it is used just to convert the string type from database to load in to html
    context={
             'data':data,
             'dob':dob
             }
    
    if request.method=="POST":
        if request.POST.get('save_edit'): #this is used to update the recruited member details
            # checks the marked check-boxes
            cash_payment_status=False
            if request.POST.get('cash_payment_status'):
                cash_payment_status=True
            ieee_payment_status=False
            if request.POST.get('ieee_payment_status'):
                ieee_payment_status=True
            
            info_dict={
                'first_name':request.POST['first_name'],
                'middle_name':request.POST['middle_name'],
                'last_name':request.POST['last_name'],
                'contact_no':request.POST['contact_no'],
                'date_of_birth':request.POST['date_of_birth'],
                'email_personal':request.POST['email_personal'],
                'facebook_url':request.POST['facebook_url'],
                'home_address':request.POST['home_address'],
                'major':request.POST['major'], 'graduating_year':request.POST['graduating_year'],
                'ieee_id':request.POST['ieee_id'],
                'recruited_by':request.POST['recruited_by'],
                'cash_payment_status':cash_payment_status,
                'ieee_payment_status':ieee_payment_status
            }
            renderData.Recruitment.updateRecruiteeDetails(nsu_id=nsu_id,values=info_dict)
    return render(request,"recruitee_details.html",context=context)


@login_required
def recruit_member(request,session_name):
    getSessionId=renderData.Recruitment.getSessionid(session_name=session_name)
    form=StudentForm
    context={
        'form':form,
        'session_name':session_name,
        'session_id':getSessionId['session'][0]['id']
    }

    
    #this method is for the POST from the recruitment form
    
    if request.method=="POST":
        
        try:
            
            cash_payment_status=False
            if request.POST.get("cash_payment_status"):
                cash_payment_status=True
            ieee_payment_status=False
            if request.POST.get("ieee_payment_status"):
                ieee_payment_status=True
                
            #getting all data from form and registering user upon validation
            recruited_member=recruited_members(
            nsu_id=request.POST['nsu_id'],
            first_name=request.POST['first_name'],
            middle_name=request.POST['middle_name'],
            last_name=request.POST['last_name'],
            contact_no=request.POST['contact_no'],
            date_of_birth=request.POST['date_of_birth'],
            email_personal=request.POST['email_personal'],
            gender=request.POST['gender'],
            facebook_url=request.POST['facebook_url'],
            home_address=request.POST['home_address'],
            major=request.POST['major'],
            graduating_year=request.POST['graduating_year'],
            session_id=getSessionId['session'][0]['id'],
            recruited_by=request.POST['recruited_by'],
            cash_payment_status=cash_payment_status,
            ieee_payment_status=ieee_payment_status
            )
            recruited_member.save() #Saving the member to the database
            messages.info(request,"Registered Member Successfully!")
            return render(request,"membership_form.html",context=context)
        
        except IntegrityError: #Checking if same id exist and handling the exception
            messages.info(request,f"Member with NSU ID: {request.POST['nsu_id']} is already registered in the database!")
            return render(request,"membership_form.html",context=context)
        
        except: #Handling all errors
            messages.info(request,"Something went Wrong! Please try again")
            return render(request,"membership_form.html",context=context)
    
    else:
        return render(request,"membership_form.html",context=context)
    