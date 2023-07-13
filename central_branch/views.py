from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import renderData
from port.models import Teams,Chapters_Society_and_Affinity_Groups
from django.db import connection
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from recruitment.models import recruited_members
import csv,datetime
from users.ActiveUser import ActiveUser
from django.db import DatabaseError
from system_administration.render_access import Access_Render
from central_branch.renderData import Branch
from events_and_management_team.renderData import Events_And_Management_Team
from logistics_and_operations_team.renderData import LogisticsTeam
from . models import Events,InterBranchCollaborations,IntraBranchCollaborations,Event_type,Event_Venue,ResearchPaper
from events_and_management_team.models import Venue_List,Permission_criteria




# Create your views here.

def central_home(request):
    user=request.user
    has_access=Access_Render.system_administrator_superuser_access(user.username)
    if (has_access):
        #renderData.Branch.test_google_form()
        return render(request,'central_home.html')
    else:
        return render(request,"access_denied2.html")

@login_required
def event_control(request):
    all_insb_events=renderData.Branch.load_all_events()
    context={
        'events':all_insb_events,
    }
    if(request.method=="POST"):
        if request.POST.get('create_new_event'):
            print("Create")
    
    return render(request,'event_page.html',context)

@login_required
def event_creation_form_page1(request):
    
    #######load data to show in the form boxes#########
    
    #loading super/mother event at first
    super_events=Branch.load_all_mother_events()
    event_types=Branch.load_all_event_type()

    
    context={
        'super_events':super_events,
        'event_types':event_types,
    }
    
    
    if(request.method=="POST"):
        if(request.POST.get('next')):
            super_event_name=request.POST.get('super_event')
            
            event_name=request.POST['event_name']
            event_description=request.POST['event_description']
            probable_date=request.POST['probable_date']
            final_date=request.POST['final_date']
            
            get_event=renderData.Branch.register_event_page1(
                super_event_name=super_event_name,
                event_name=event_name,
                event_description=event_description,
                probable_date=probable_date,
                final_date=final_date)
            
            if(get_event)==False:
                messages.info(request,"Database Error Occured! Please try again later.")
            else:
                #if the method returns true, it will redirect to the new page
                return redirect('central_branch:event_creation_form2',get_event)


                
            
                
        elif(request.POST.get('cancel')):
            return redirect('central_branch:event_control')
    return render(request,'event_creation_form1.html',context)

@login_required
def event_creation_form_page2(request,event_id):
    #loading all inter branch collaboration Options
    inter_branch_collaboration_options=Branch.load_all_inter_branch_collaboration_options()
    context={
        'inter_branch_collaboration_options':inter_branch_collaboration_options,
    }
    if request.method=="POST":
        if(request.POST.get('next')):
            inter_branch_collaboration_list=request.POST.getlist('inter_branch_collaboration')
            intra_branch_collaboration=request.POST['intra_branch_collaboration']
            
            if(renderData.Branch.register_event_page2(
                inter_branch_collaboration_list=inter_branch_collaboration_list,
                intra_branch_collaboration=intra_branch_collaboration,
                event_id=event_id)):
                return redirect('central_branch:event_creation_form3',event_id)
            else:
                messages.info(request,"Database Error Occured! Please try again later.")

        elif(request.POST.get('cancel')):
            return redirect('central_branch:event_control')


    return render(request,'event_creation_form2.html',context)

def event_creation_form_page3(request,event_id):
    #loading all venues from the venue list from event management team database
    venues=Events_And_Management_Team.getVenues()
    #loading all the permission criterias from event management team database
    permission_criterias=Events_And_Management_Team.getPermissionCriterias()

    context={
        'venues':venues,
        'permission_criterias':permission_criterias,
    }
    if request.method=="POST":
        if request.POST.get('next'):
            #getting the venues for the event
            venue_list_for_event=request.POST.getlist('event_venues')
            #getting the permission criterias for the event
            permission_criterias_list_for_event=request.POST.getlist('permission_criteria')
            
            #updating data collected from part3 for the event
            update_event_details=renderData.Branch.register_event_page3(venue_list=venue_list_for_event,permission_criteria_list=permission_criterias_list_for_event,event_id=event_id)
            #if return value is false show an error message
            if(update_event_details==False):
                messages.info(request, "An error Occured! Please Try again!")
            else:
                return redirect('central_branch:event_control')

    return render(request,'event_creation_form3.html',context)


def event_control_homepage(request,event_id):
    
    return render(request,'event_control_homepage.html')

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
                #ADDING MEMBER TO TEAM
                for member in members_to_add:
                    if(renderData.Branch.add_member_to_team(ieee_id=member,team=pk,position=position)):
                        messages.info(request,"Member Added to the team!")
                    elif(renderData.Branch.add_member_to_team(ieee_id=member,team=pk,position=position)==False):
                        messages.info(request,"Member couldn't be added!")
                    elif(renderData.Branch.add_member_to_team(ieee_id=member,team=pk,position=position)==DatabaseError):
                        messages.info(request,"An internal Database Error Occured! Please try again!")
                return redirect('central_branch:team_details',pk,name)

    context={
        'team_name':name,
        'team_members':team_members,
        'positions':positions,
        'insb_members':insb_members,
        
    }
    return render(request,'team_details_page.html',context=context)
@login_required
def event_dashboard(request,event_id):
    '''Details page for registered events'''
    
    context={}
    get_all_team_name = renderData.Branch.load_teams()
    get_event_details = Events.objects.get(id = event_id)
    get_inter_branch_collaboration = InterBranchCollaborations.objects.filter(event_id=get_event_details.id)
    get_intra_branch_collaboration = IntraBranchCollaborations.objects.filter(event_id = get_event_details.id)
    get_event_venue = Event_Venue.objects.filter(event_id = get_event_details.id)  
    if request.method == "POST":
        team_under = request.POST.get('team_under')
        member_under = request.POST.get('memeber_under')
        probable_date = request.POST.get('probable_date')
        progress = request.POST.get('progression')    
    context={
        'event_details':get_event_details,
        'inter_branch_details':get_inter_branch_collaboration,
        'intra_branch_details':get_intra_branch_collaboration,
        'event_venue':get_event_venue,
        'team_names':get_all_team_name
    }
    return render(request,"event_dashboard.html",context)

@login_required
def others(request):
    return render(request,"others.html")
@login_required
def add_research(request):
    if request.method == "POST":
        if request.POST.get('title') == "" or request.POST.get('author_name') == "" or request.POST.get('url')=="":
            return render(request,"research_papers.html",{
                "error":True
            })
        else:
            title = request.POST.get('title')
            author_names = request.POST.get('author_name')
            research_pic = request.POST.get('filename')
            url = request.POST.get('url')
            save_research_paper = ResearchPaper(Title=title,Research_picture=research_pic,Author_names=author_names,Publication_link=url)
            save_research_paper.save()
            return render(request,"research_papers.html",{
                "saved":True
            })

    return render(request,"research_papers.html")