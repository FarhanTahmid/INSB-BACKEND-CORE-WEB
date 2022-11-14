from django.shortcuts import render
from django.db import DatabaseError
from recruitment.models import recruitment_session,recruited_members
from . import renderData
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def recruitment_home(request):
    numberOfSessions=renderData.Recruitment.loadSession()
    if request.method=="POST":
        session_name=request.POST["recruitment_session"]
        try:
            add_session=recruitment_session(session=session_name)
            add_session.save()
        except DatabaseError:
            print("error happened")
    return render(request,'recruitment_home.html',numberOfSessions)

def recruitee(request):
    if request.method=="POST":
        session_id=request.POST["get_recruited_members"]
        getSession=renderData.Recruitment.getSession(session_id=session_id)
        getRecruitedMembers=renderData.Recruitment.getRecruitedMembers(session_id=session_id)
        
        context={
            'session':getSession,
            'members':getRecruitedMembers
        }
        print(context['members']['member'][0]['nsu_id'])
        return render(request,'recruitees.html',context)
    return render(request,'recruitees.html')
