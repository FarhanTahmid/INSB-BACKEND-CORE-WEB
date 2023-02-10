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
from django.db import DatabaseError
from system_administration.render_access import Access_Render
from insb_central.renderData import Branch
from events_and_management_team.renderData import Events_And_Management_Team
from logistics_and_operations_team.renderData import LogisticsTeam
from . models import Events,InterBranchCollaborations,IntraBranchCollaborations


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
    
    if(request.method=="POST"):
        if request.POST.get('create_new_event'):
            print("Create")
    
    return render(request,'event_page.html')

@login_required
def event_creation_form_page1(request):
    
    #######load data to show in the form boxes#########
    
    #loading super/mother event at first
    super_events=Branch.load_all_mother_events()
    
    #loading all venues from the venue list from event management team database
    venues=Events_And_Management_Team.getVenues()
    #loading all the permission criterias from event management team database
    permission_criterias=Events_And_Management_Team.getPermissionCriterias()

    
    context={
        'super_events':super_events,
        
        'venues':venues,
        'permission_criterias':permission_criterias,
    }
    
    if(request.method=="POST"):
        if(request.POST.get('next')):
            super_event_name=request.POST.get('super_event')
            
            if(super_event_name=="null"):
                
                #now create the event as super event is null
                event_name=request.POST['event_name']
                event_description=request.POST['event_description']
                probable_date=request.POST['probable_date']
                final_date=request.POST['final_date']
                
                if(final_date==''):
                    
                    try:
                        new_event=Events(
                        super_event_name=super_event_name,
                        event_name=event_name,
                        event_description=event_description,
                        probable_date=probable_date
                        )
                        new_event.save()
                        return redirect('insb_central:event_creation_form2',new_event.id)
                    except:
                        messages.info(request,"Database Error Occured! Please try again later.")
                else:
                    try:
                        new_event=Events(
                        super_event_name=super_event_name,
                        event_name=event_name,
                        event_description=event_description,
                        probable_date=probable_date,
                        final_date=final_date
                        )
                        new_event.save()
                        return redirect('insb_central:event_creation_form2',new_event.id)
                    except:
                        messages.info(request,"Database Error Occured! Please try again later.")    
            else:
                 #now create the event as super event in the event models
                
                event_name=request.POST['event_name']
                event_description=request.POST['event_description']
                probable_date=request.POST['probable_date']
                final_date=request.POST['final_date']
                
                if(final_date==''):
                    
                    try:
                        new_event=Events(
                        super_event_name=super_event_name,
                        event_name=event_name,
                        event_description=event_description,
                        probable_date=probable_date
                        )
                        new_event.save()
                        return redirect('insb_central:event_creation_form2',new_event.id)
                    except:
                        messages.info(request,"Database Error Occured! Please try again later.")
                else:
                    try:
                        new_event=Events(
                        super_event_name=super_event_name,
                        event_name=event_name,
                        event_description=event_description,
                        probable_date=probable_date,
                        final_date=final_date
                        )
                        new_event.save()
                        return redirect('insb_central:event_creation_form2',new_event.id)
                    except:
                        messages.info(request,"Database Error Occured! Please try again later.")    
        elif(request.POST.get('cancel')):
            return redirect('insb_central:event_control')
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
            
            #first check if both the collaboration options are null. If so, do register nothing on database and redirect to the next page
            if(inter_branch_collaboration_list[0]=="null" and intra_branch_collaboration==""):
                print("Dont collab for anything") #go to the third page
            #check if any intra branch collab is entered while inter branch collab option is still set to null. If so, then only register for intra branch collaboration option
            elif(inter_branch_collaboration_list[0]=="null" and intra_branch_collaboration!=""):
                print("Do the intra branch collab only")
            #now checking for the criterias where there are inter branch collaboration
            else:
                #checking if the intra branch collab option is still null. If null, only register for intra branch collaboration
                if(intra_branch_collaboration==""):
                    for id in inter_branch_collaboration_list:
                        print(f"Do inter branch collab for {id}")
                #now register for the both collaboration option when both are filled
                else:
                    print("Do collab for both")

        elif(request.POST.get('cancel')):
            return redirect('insb_central:event_control')


    return render(request,'event_creation_form2.html',context)



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
                return redirect('insb_central:team_details',pk,name)

    context={
        'team_name':name,
        'team_members':team_members,
        'positions':positions,
        'insb_members':insb_members,
        
    }
    return render(request,'team_details_page.html',context=context)