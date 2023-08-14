from django.shortcuts import render
from . import renderData
from meeting_minutes.renderData import team_mm_info,branch_mm_info

# Create your views here.
def meeting_minutes_homepage(request):
    return render(request,'meeting_minutes_homepage.html')

def team_meeting_minutes(request):
    '''
    Loads all the teams' exisitng meeting minutes
    Gives option to add or delete a meeting minutes
    '''
    
    #load teams' meeting minutes from database
    
    teams_mm=renderData.team_meeting_minutes.load_all_team_mm()
    team_mm_list=[]
    for team in teams_mm:
        team_mm_list.append(team)
    context={
        'team':team_mm_list
    }

    return render(request,'team_meeting_minutes.html')


def branch_meeting_minutes(request):
    '''
    Loads all the branchs' existing meeting minutes
    Gives option to add or delete a meeting minutes
    '''
    
    #load branchs' meeting minutes from database
    
    branch_mm=renderData.branch_meeting_minutes.load_all_branch_mm()
    branch_mm_list=[]
    for branch in branch_mm:
        branch_mm_list.append(branch)
    context={
        'team':branch_mm_list
    }
    return render(request,'branch_meeting_minutes.html')


