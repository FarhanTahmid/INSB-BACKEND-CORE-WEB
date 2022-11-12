from django.shortcuts import render
from . import renderData
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def recruitment_home(request):
    numberOfSessions=renderData.Recruitment.loadSession()
    return render(request,'recruitment_home.html',numberOfSessions)
