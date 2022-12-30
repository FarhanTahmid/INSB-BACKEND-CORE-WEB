from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import renderData
from port.models import Teams
from django.db import connection
from django.db.utils import IntegrityError
from recruitment.models import recruited_members
import csv,datetime
from users.ActiveUser import ActiveUser

# Create your views here.
def central_home(request):
    return render(request,'central_home.html')
def event_control(request):
    return render(request,'event_control_page.html')
def teams(request):
    
    '''
    Loads all the existing teams in the branch
    Gives option to add or delete a team
    '''
    
    #load teams from database
    
    teams=renderData.Branch.load_teams()
    team_list=[]
    for team in teams:
        team_list.append(team)
    context={
        'team':team_list
    }
    
    return render(request,'teams.html',context=context)
def team_details(request,pk,name):
    
    '''Detailed panel for the team'''
    
    #load data of current team Members
    team_members=renderData.Branch.load_team_members(pk)
    #load all the roles and positions from database
    positions=renderData.Branch.load_roles_and_positions()
    #loading all members of insb
    insb_members=renderData.Branch.load_all_insb_members()
    
    members_to_add=[]
    position=12 #assigning default to volunteer
    if request.method=='POST':
        if(request.POST.get('add_to_team')):
            #Checking if a button is clicked
            if(request.POST.get('member_select')):
                members_to_add=request.POST.getlist('member_select')
                position=request.POST.get('position')
     
    context={
        'team_name':name,
        'team_members':team_members,
        'positions':positions,
        'insb_members':insb_members,
        
    }
    return render(request,'team_details_page.html',context=context)