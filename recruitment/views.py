from django.shortcuts import render
from django.db import DatabaseError
from recruitment.models import recruitment_session,recruited_members
from . import renderData
from django.contrib.auth.decorators import login_required
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
    print(pk)
    getRecruitedMembers=renderData.Recruitment.getRecruitedMembers(session_id=pk)
    context={
        'session':getSession,
        'members':getRecruitedMembers,
       }
    print(context)
    return render(request,'recruitees.html',context=context)


@login_required
def recruitee_details(request,nsu_id):
    return render(request,"recruitee_details.html")

@login_required
def recruit_member(request):
    return render(request,"membership_form.html")