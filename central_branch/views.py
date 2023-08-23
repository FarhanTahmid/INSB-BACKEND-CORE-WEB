from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.http import JsonResponse, response
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import renderData
from port.models import Teams,Chapters_Society_and_Affinity_Groups,Roles_and_Position
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
from . models import Events,InterBranchCollaborations,IntraBranchCollaborations,Event_type,Event_Venue,SuperEvents
from events_and_management_team.models import Venue_List,Permission_criteria
from main_website.models import Research_Papers,Blog_Category,Blog
from users.models import Members




# Create your views here.

def central_home(request):
    user=request.user
    has_access=Access_Render.system_administrator_superuser_access(user.username)
    if (has_access):
        #renderData.Branch.test_google_form()'''
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
    
    return render(request,'event/event_page.html',context)

@login_required
def super_event_creation(request):

    '''function for creating super event'''

    if request.method == "POST":

        '''Checking to see if either of the submit or cancelled button has been clicked'''

        if (request.POST.get('Submit')):

            '''Getting data from page and saving them in database'''

            super_event_name = request.POST.get('super_event_name')
            super_event_description = request.POST.get('super_event_description')
            start_date = request.POST.get('probable_date')
            end_date = request.POST.get('final_date')
            saving_data = SuperEvents(super_event_name=super_event_name,super_event_description=super_event_description,start_date=start_date,end_date=end_date)
            saving_data.save()
            return redirect('central_branch:event_control')
        
        elif (request.POST.get('cancel')):
            return redirect('central_branch:event_control')
        
    return render(request,"event/super_event_creation_form.html")


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
            event_type = request.POST['event_type']
            probable_date=request.POST['probable_date']
            final_date=request.POST['final_date']
    
            
            get_event=renderData.Branch.register_event_page1(
                super_event_name=super_event_name,
                event_name=event_name,
                event_type=event_type,
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
    return render(request,'event/event_creation_form1.html',context)

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


    return render(request,'event/event_creation_form2.html',context)

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

    return render(request,'event/event_creation_form3.html',context)

@login_required
def event_dashboard(request,event_id):

    '''Checking to see whether the user has access to view events on portal and edit them'''
    user = request.user
    has_access = renderData.Branch.event_page_access(user)
    if has_access:

        '''Details page for registered events'''
    
        context={}
        get_all_team_name = renderData.Branch.load_teams()
        get_event_details = Events.objects.get(id = event_id)
        #print(get_event_details.super_event_name.id)
        get_inter_branch_collaboration = InterBranchCollaborations.objects.filter(event_id=get_event_details.id)
        get_intra_branch_collaboration = IntraBranchCollaborations.objects.filter(event_id = get_event_details.id)
        get_event_venue = Event_Venue.objects.filter(event_id = get_event_details.id)  
        
        if request.method == "POST":
            #FOR TASK ASSIGNING
            team_under = request.POST.get('team')
            team_member = request.POST.get('team_member')
            probable_date = request.POST.get('probable_date')
            progress = request.POST.get('progression')    
        context={
            'event_details':get_event_details,
            'inter_branch_details':get_inter_branch_collaboration,
            'intra_branch_details':get_intra_branch_collaboration,
            'event_venue':get_event_venue,
            'team_names':get_all_team_name
        }
    else:
        return redirect('main_website:all-events')
    return render(request,"event/event_dashboard.html",context)

@login_required
def get_updated_options_for_event_dashboard(request):
    #this function updates the select box upon the selection of the team in task assignation. takes event id as parameter. from html file, a script hits the api and fetches the returned dictionary
    
    if request.method == 'GET':
        # Retrieve the selected value from the query parameters
        selected_team = request.GET.get('team_id')

        # fetching the team member
        members=renderData.Branch.load_team_members(selected_team)
        updated_options = [
            # Add more options as needed
        ]
        for member in members:
            updated_options.append({'value': member.ieee_id, 'member_name': member.name,'position':member.position.role})

        #returning the dictionary
        return JsonResponse(updated_options, safe=False)

def event_control_homepage(request,event_id):
    
    return render(request,'event_control_homepage.html')

#Panel and Team Management
def teams(request):
    
    '''
    Loads all the existing teams in the branch
    Gives option to add or delete a team
    '''
    #load panel lists
    panels=renderData.Branch.load_ex_com_panel_list()
    user = request.user

    '''Checking if user is EB/faculty or not, and the calling the function event_page_access
    which was previously called for providing access to Eb's/faculty only to event page'''

    has_access = renderData.Branch.event_page_access(user)
    if has_access:
        '''
        Loads all the existing teams in the branch
        Gives option to add or delete a team
        '''
        if request.method == "POST":
            if request.POST.get('recruitment_session'):
                team_name = request.POST.get('recruitment_session')
                new_team = Teams(team_name = team_name)
                new_team.save()
    
        #load teams from database
    
        teams=renderData.Branch.load_teams()
        team_list=[]
        for team in teams:
            team_list.append(team)
        context={
            'team':team_list,
        }
        return render(request,'team/teams.html',context=context)
    return render(request,"access_denied2.html")


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
        if(request.POST.get('remove_member')):
            '''To remove member from team table'''
            try:
                Members.objects.filter(ieee_id=request.POST['access_ieee_id']).update(team=None,position=Roles_and_Position.objects.get(id=13))
                return redirect('central_branch:team_details',pk,name)
            except:
                pass
        if (request.POST.get('update')):
            '''To update member's position in a team'''
            ieee_id=request.POST.get('access_ieee_id')
            position = request.POST.get('position')
            Members.objects.filter(ieee_id = ieee_id).update(position = position)
            return redirect('central_branch:team_details',pk,name)
        if (request.POST.get('reset_team')):
            '''To remove all members in the team and assigning them as general memeber'''
            all_memebers_in_team = Members.objects.filter(team = pk)
            all_memebers_in_team.update(team=None,position = Roles_and_Position.objects.get(id=13))
            return redirect('central_branch:team_details',pk,name)

            
            



    
    context={
        'team_id':pk,
        'team_name':name,
        'team_members':team_members,
        'positions':positions,
        'insb_members':insb_members,
        
    }
    return render(request,'team/team_details_page.html',context=context)

@login_required
def manage_team(request,pk,team_name):
    context={
        'team_id':pk,
        'team_name':team_name,
    }
    return render(request,'team/team_management.html',context=context)

#PANEL WORS
@login_required
def panel_details(request,pk):
    return render(request,"ex_com_panels/panel_details.html")

@login_required
def others(request):
    return render(request,"others.html")

@login_required
def add_research(request):


    '''function for adding new Research paper'''


    if request.method == "POST":

        '''Checking to see if all the mandatory fields have been entered by user or not once
        the submit button has been clicked. If not then sending error message to the page else
        render data to the page'''
        
        if request.POST.get('title') == "" or request.POST.get('author_name') == "" or request.POST.get('url')=="":
            return render(request,"research_papers.html",{
                "error":True
            })
        else:
            title = request.POST.get('title')
            author_names = request.POST.get('author_name')
            research_banner_pic = request.POST.get('research_banner_picture')
            url = request.POST.get('url')
            save_research_paper = Research_Papers(title=title,research_banner_picture=research_banner_pic,author_names=author_names,publication_link=url)
            save_research_paper.save()
            return render(request,"research_papers.html",{
                "saved":True
            })

    return render(request,"research_papers.html")

@login_required
def add_blogs(request):

    '''function to add new blog to the page'''

    load_blog_category = Blog_Category.objects.all()
    load_Chapters_Society_And_Affinity_Groups = Chapters_Society_and_Affinity_Groups.objects.all()

    '''When the submit button is clicked'''

    if request.method=="POST":

        '''Checking for essential fields to be filled. If incomplete, error will be loaded
        on the form page'''

        if request.POST.get('title') == "" or request.POST.get('date') == ""  or request.POST.get('Pname') == "" or request.POST.get('description')== "":
            return render(request,"add_blogs.html",{
                "error":True,
                "category":load_blog_category,
                "chapterSocietyAndAffinityGroups":load_Chapters_Society_And_Affinity_Groups
            }) 
        else:
            title =  request.POST.get('title')
            date = request.POST.get('date')
            blog_pic = request.FILES['filename']
            category = request.POST.get('category')
            publisherName = request.POST.get('Pname')
            chapterSocietyAndAffinityGroups = request.POST.get('chapterSocietyAndAffinityGroups')
            description = request.POST.get('description')

            '''Checking conditions regarding when either of the two fields is empty or full
            and saving the data to the database on the basis of the conditions, where other fields
            apart from category and chapterSocietyAndAffinityGroups is mandatorys'''

            if category=="" and chapterSocietyAndAffinityGroups!="":
                chapterSocietyAndAffinityGroups = Chapters_Society_and_Affinity_Groups.objects.get(id=chapterSocietyAndAffinityGroups)
                save_blog = Blog(title=title,date=date,blog_banner_picture=blog_pic,publisher = publisherName,chapter_society_affinity=chapterSocietyAndAffinityGroups,description=description)
                save_blog.save()
            elif category!="" and chapterSocietyAndAffinityGroups=="":
                category = Blog_Category.objects.get(id=category)
                save_blog = Blog(title=title,date=date,blog_banner_picture=blog_pic,publisher = publisherName,category=category,description=description)
                save_blog.save()
            elif category=="" and chapterSocietyAndAffinityGroups=="":
                    save_blog = Blog(title=title,date=date,blog_banner_picture=blog_pic,publisher = publisherName,description=description)
                    save_blog.save()
            else:
                category = Blog_Category.objects.get(id=category)
                chapterSocietyAndAffinityGroups = Chapters_Society_and_Affinity_Groups.objects.get(id=chapterSocietyAndAffinityGroups)
                save_blog = Blog(title=title,date=date,blog_banner_picture=blog_pic,publisher = publisherName,category=category,chapter_society_affinity=chapterSocietyAndAffinityGroups,description=description)
                save_blog.save()
            
            return render(request,"add_blogs.html",{
                "saved":True,
                "category":load_blog_category,
                "chapterSocietyAndAffinityGroups":load_Chapters_Society_And_Affinity_Groups
            })
    return render(request,"add_blogs.html",{
        "category":load_blog_category,
        "chapterSocietyAndAffinityGroups":load_Chapters_Society_And_Affinity_Groups
    })

