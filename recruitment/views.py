from django.shortcuts import render
from django.db import DatabaseError
from recruitment.models import recruitment_session
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
        return render(request,'recruitees.html')
    return render(request,'recruitees.html')
