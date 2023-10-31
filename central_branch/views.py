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
from django.conf import settings
from users.renderData import LoggedinUser
import os
from users import renderData as port_render
from port.renderData import PortData
from users.renderData import PanelMembersData


# Create your views here.

def central_home(request):
    user=request.user
    has_access=Access_Render.system_administrator_superuser_access(user.username)
    if (has_access):
        #renderData.Branch.test_google_form()'''
        return render(request,'homepage/branch_homepage.html')
        # return render(request,'central_home.html')

    else:
        return render(request,"access_denied2.html")

@login_required
def event_control_homepage(request):
    # This function loads all events and super events in the event homepage table
    all_insb_events=renderData.Branch.load_all_events()
    context={
        'events':all_insb_events,
    }
    if(request.method=="POST"):
        if request.POST.get('create_new_event'):
            print("Create")
    
    return render(request,'Events/event_homepage.html',context)

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
def event_creation_form_page(request):
    
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
            event_date=request.POST['event_date']
    
            
            get_event=renderData.Branch.register_event_page1(
                super_event_name=super_event_name,
                event_name=event_name,
                event_type=event_type,
                event_description=event_description,
                event_date=event_date
            )
            
            if(get_event)==False:
                messages.info(request,"Database Error Occured! Please try again later.")
            else:
                #if the method returns true, it will redirect to the new page
                return redirect('central_branch:event_creation_form2',get_event)

        elif(request.POST.get('cancel')):
            return redirect('central_branch:event_control')
    return render(request,'Events/event_creation_form.html',context)

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


    return render(request,'Events/event_creation_form2.html',context)

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
        if request.POST.get('create_event'):
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

    return render(request,'Events/event_creation_form3.html',context)

@login_required
def event_description(request,event_id):

    '''Checking to see whether the user has access to view events on portal and edit them'''
    user = request.user
    has_access = renderData.Branch.event_page_access(user)
    if has_access:

        '''Details page for registered events'''

        # Get collaboration details
        interBranchCollaborations=Branch.event_interBranch_Collaborations(event_id=event_id)
        intraBranchCollaborations=Branch.event_IntraBranch_Collaborations(event_id=event_id)
        # Checking if event has collaborations
        hasCollaboration=False
        if(len(interBranchCollaborations)>0 and len(intraBranchCollaborations)>0):
            hasCollaboration=True
        
        

        get_all_team_name = renderData.Branch.load_teams()
        get_event_details = Events.objects.get(id = event_id)

        #print(get_event_details.super_event_name.id)
        get_event_venue = Event_Venue.objects.filter(event_id = get_event_details.id)  
        
        if request.method == "POST":
            #FOR TASK ASSIGNING
            team_under = request.POST.get('team')
            team_member = request.POST.get('team_member')
            probable_date = request.POST.get('probable_date')
            progress = request.POST.get('progression')    
        context={
            'event_details':get_event_details,
            'event_venue':get_event_venue,
            'team_names':get_all_team_name,
            'interBranchCollaborations':interBranchCollaborations,
            'intraBranchCollaborations':intraBranchCollaborations,
            'hasCollaboration':hasCollaboration,
        }
    else:
        return redirect('main_website:all-events')
    return render(request,"Events/event_description.html",context)

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



#Panel and Team Management
def teams(request):
    
    '''
    Loads all the existing teams in the branch
    Gives option to add or delete a team
    '''
    #load panel lists
    # panels=renderData.Branch.load_ex_com_panel_list()
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
            if (request.POST.get('reset_all_teams')):
                '''To remove all members in all teams and assigning them as general memeber'''
                all_memebers_in_team = Members.objects.all()
                all_memebers_in_team.update(team=None,position = Roles_and_Position.objects.get(id=13))
                return redirect('central_branch:teams')
    
        #load teams from database
    
        teams=renderData.Branch.load_teams()
        team_list=[]
        for team in teams:
            team_list.append(team)
            
        context={
            'team':team_list,
        }
        return render(request,'Teams/team_homepage.html',context=context)
    return render(request,"access_denied2.html")


def team_details(request,primary,name):
    
    '''Detailed panel for the team'''
    
    #load data of current team Members
    team_members=renderData.Branch.load_team_members(primary)
    #load all the roles and positions from database
    positions=renderData.Branch.load_roles_and_positions()
    # Excluding position of EB, Faculty and SC-AG members
    for i in positions:
        if(i.is_eb_member or i.is_faculty or i.is_sc_ag_eb_member):
            positions=positions.exclude(pk=i.pk)
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
                    if(renderData.Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position)):
                        messages.info(request,"Member Added to the team!")
                    elif(renderData.Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position)==False):
                        messages.info(request,"Member couldn't be added!")
                    elif(renderData.Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position)==DatabaseError):
                        messages.info(request,"An internal Database Error Occured! Please try again!")
                return redirect('central_branch:team_details',primary,name)
        if(request.POST.get('remove_member')):
            '''To remove member from team table'''
            try:
                Members.objects.filter(ieee_id=request.POST['access_ieee_id']).update(team=None,position=Roles_and_Position.objects.get(id=13)) #ID 13 means general member
                return redirect('central_branch:team_details',primary,name)
            except:
                pass
        if (request.POST.get('update')):
            '''To update member's position in a team'''
            ieee_id=request.POST.get('access_ieee_id')
            position = request.POST.get('position')
            Members.objects.filter(ieee_id = ieee_id).update(position = position)
            return redirect('central_branch:team_details',primary,name)
        
        if (request.POST.get('reset_team')):
            print("got request")
            '''To remove all members in the team and assigning them as general memeber'''
            all_memebers_in_team = Members.objects.filter(team = Teams.objects.get(primary=primary))
            all_memebers_in_team.update(team=None,position = Roles_and_Position.objects.get(id=13))
            return redirect('central_branch:team_details',primary,name)
        
    context={
        'team_id':primary,
        'team_name':name,
        'team_members':team_members,
        'positions':positions,
        'insb_members':insb_members,
        
    }
    # return render(request,'team/team_details_page.html',context=context)
    return render(request,'Teams/team_details.html',context=context)

@login_required
def manage_team(request,pk,team_name):
    context={
        'team_id':pk,
        'team_name':team_name,
    }
    return render(request,'team/team_management.html',context=context)

#PANEL WORkS
@login_required
def panel_home(request):
    
    # get all panels from database
    panels = Branch.load_all_panels()
    
    if request.method=="POST":
        tenure_year=request.POST['tenure_year']
        current_check=request.POST.get('current_check')
        # create panel
        if(Branch.create_panel(request,tenure_year=tenure_year,current_check=current_check)):
            return redirect('central_branch:panels')
        
    context={
        'panels':panels,
    }
    
    return render(request,"Panel/panel_homepage.html",context)

@login_required
def panel_details(request,panel_id):
    # Load the panel information
    panel_info = Branch.load_panel_by_id(panel_id)
    # Load the Members data associated with the panel
    panel_members=Branch.load_panel_members_by_panel_id(panel_id=panel_id)
    # Creating list to get different types of members
    eb_member=[]
    officer_member=[]
    faculty_member=[]
    volunteer_members=[]
    
    for i in panel_members:
        # if the member position is eb_member
        if(i.position.is_eb_member):
            eb_member.append(i)
        # if the member position is officer member
        elif(i.position.is_officer):
            officer_member.append(i)
        # if the member position is faculty member
        elif(i.position.is_faculty):
            faculty_member.append(i)
        else:
        # generally add rest of the members as volunteers as one can only be added to Panel Member list if he is in any position or team. 
            volunteer_members.append(i)
    
    all_insb_members=port_render.get_all_registered_members(request)

    if request.method=="POST":
        '''Block of code for Executive Members'''
        # Check whether the add executive button was pressed
        if (request.POST.get('add_executive_to_panel')):
            # get position
            position=request.POST.get('position')
            # get members as list
            members=request.POST.getlist('member_select')

            if(PanelMembersData.add_members_to_branch_panel(request=request,members=members,panel_info=panel_info,position=position,team_primary=1)): #team_primary=1 as branchs primary is always 1
                return redirect('central_branch:panel_details',panel_id)
            
        # check whether the remove member button was pressed
        if (request.POST.get('remove_member')):
            # get ieee_id of the member
            ieee_id=request.POST['remove_panel_member']
            # remove member
            if(PanelMembersData.remove_member_from_panel(request=request,ieee_id=ieee_id,panel_id=panel_info.pk)):
                return redirect('central_branch:panel_details',panel_id)
        
        '''Block of code for Officer Members'''

        # Check whether the add officer button was pressed
        if(request.POST.get('add_officer_to_panel')):
            # get position
            position=request.POST.get('position1')
            # get team
            team=request.POST.get('team')
            # get members as a list
            members=request.POST.getlist('member_select1')

            if(PanelMembersData.add_members_to_branch_panel(request=request,members=members,panel_info=panel_info,position=position,team_primary=team)):
                return redirect('central_branch:panel_details',panel_id)
        
        if(request.POST.get('remove_member_officer')):
            # get ieee_id of the member
            ieee_id=request.POST['remove_officer_member']
            # remove member
            if(PanelMembersData.remove_member_from_panel(request=request,ieee_id=ieee_id,panel_id=panel_info.pk)):
                return redirect('central_branch:panel_details',panel_id)

        





    all_insb_executive_positions=PortData.get_all_executive_positions_with_sc_ag_id(request,sc_ag_primary=1) #setting sc_ag_primary as 1, because Branch's Primary is 1 by default
    all_insb_officer_positions=PortData.get_all_officer_positions_with_sc_ag_id(request,sc_ag_primary=1)
    all_insb_teams=PortData.get_teams_of_sc_ag_with_id(request,sc_ag_primary=1)
    context={
        'panel_info':panel_info,
        'eb_member':eb_member,
        'officer_member':officer_member,
        'faculty_member':faculty_member,
        'volunteer_members':volunteer_members,
        'insb_members':all_insb_members,
        'positions':all_insb_executive_positions,
        'officer_positions':all_insb_officer_positions,
        'teams':all_insb_teams,
    }
    return render(request,'Panel/panel_details.html',context)


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


from main_website.models import HomePageTopBanner
@login_required
def manage_website_homepage(request):
    '''For top banner picture with Texts and buttons - Tab 1'''
    topBannerItems=HomePageTopBanner.objects.all()
    # get user data
    #Loading current user data from renderData.py
    current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file
    if(user_data==False):
        return DatabaseError
    
    
    # Getting Form response
    if request.method=="POST":

        # To delete an item
        if request.POST.get('delete'):
            # Delelte the item. Getting the id of the item from the hidden input value.
            HomePageTopBanner.objects.filter(id=request.POST.get('get_item')).delete()
            return redirect('central_branch:manage_website_home')
        # To add a new Banner Item
        if request.POST.get('add_banner'):
            try:
                newBanner=HomePageTopBanner.objects.create(
                    banner_picture=request.FILES['banner_picture'],
                    first_layer_text=request.POST['first_layer_text'],
                    second_layer_text=request.POST['second_layer_text'],
                    second_layer_text_colored=request.POST['second_layer_text_colored'],
                    third_layer_text=request.POST['third_layer_text'],
                    button_text=request.POST['button_text'],
                    button_url=request.POST['button_url']
                )
                newBanner.save()
                messages.success(request,"New Banner Picture added in Homepage successfully!")
                return redirect('central_branch:manage_website_home')
            except:
                print("GG")


    '''For banner picture with Texts'''   
    from main_website.models import BannerPictureWithStat

    existing_banner_picture_with_numbers=BannerPictureWithStat.objects.all()
    if request.method=="POST":
        if request.POST.get('update_banner'):
            # first get all the objects and get the image file path. Delete the files from the system and then delete the object, then get the new image and create a new object.
            try:
                banner_image=request.FILES['banner_picture_with_stat']
                
                # Now get previous instances of Banner Picture with stat
                for i in BannerPictureWithStat.objects.all():
                    image_instance=settings.MEDIA_ROOT+str(i.image)
                    if(os.path.isfile(image_instance)):
                        # Delete the image now:
                        os.remove(image_instance)
                        # Now delete the object:
                        i.delete()
                
                newBannerPictureWithStat=BannerPictureWithStat.objects.create(image=banner_image)
                newBannerPictureWithStat.save()
                messages.success(request,"Banner Picture With Statistics was successfully updated")
                return redirect('central_branch:manage_website_home')    
            except Exception as e:
                messages.error(request,"Something went wrong! Please try again.")
                return redirect('central_branch:manage_website_home')    

    
    context={
        'user_data':user_data,
        'topBannerItems':topBannerItems,
        'bannerPictureWithNumbers':existing_banner_picture_with_numbers,
        'media_url':settings.MEDIA_URL
    }
    return render(request,'Manage Website/Homepage/manage_web_homepage.html',context)