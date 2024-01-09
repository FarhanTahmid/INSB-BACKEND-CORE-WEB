import logging
import traceback
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from central_events.models import Event_Category, Event_Venue, Events, SuperEvents
from content_writing_and_publications_team.forms import Content_Form
from content_writing_and_publications_team.renderData import ContentWritingTeam
from events_and_management_team.renderData import Events_And_Management_Team
from graphics_team.models import Graphics_Banner_Image, Graphics_Link
from graphics_team.renderData import GraphicsTeam
from main_website.renderData import HomepageItems
from media_team.models import Media_Images, Media_Link
from media_team.renderData import MediaTeam
from system_administration.system_error_handling import ErrorHandling
from . import renderData
from port.models import Teams,Chapters_Society_and_Affinity_Groups,Roles_and_Position,Panels
from django.db import DatabaseError
from central_branch.renderData import Branch
from main_website.models import Research_Papers,Blog_Category,Blog
from users.models import Members,Panel_Members
from django.conf import settings
from users.renderData import LoggedinUser
import os
from users import renderData as port_render
from port.renderData import PortData
from users.renderData import PanelMembersData,Alumnis
from . view_access import Branch_View_Access
from datetime import datetime
from django.utils.datastructures import MultiValueDictKeyError
from users.renderData import Alumnis
from django.http import Http404,HttpResponseBadRequest
import logging
import traceback
from chapters_and_affinity_group.get_sc_ag_info import SC_AG_Info
from central_events.forms import EventForm
from .forms import *
from .website_render_data import MainWebsiteRenderData
from django.views.decorators.clickjacking import xframe_options_exempt
import port.forms as PortForms


# Create your views here.
logger=logging.getLogger(__name__)

def central_home(request):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        context={
            'all_sc_ag':sc_ag,
        }
        user=request.user
        # has_access=Access_Render.system_administrator_superuser_access(user.username)
        if (True):
            #renderData.Branch.test_google_form()'''
            return render(request,'homepage/branch_homepage.html',context)
            # return render(request,'central_home.html')

        else:
            return render(request,"access_denied2.html")
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")


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
    
    '''Loads all the existing teams in the branch
        Gives option to add or delete a team
    '''
    sc_ag=PortData.get_all_sc_ag(request=request)
        
    if request.method == "POST":
        if request.POST.get('recruitment_session'):
            team_name = request.POST.get('recruitment_session')
            Branch.new_recruitment_session(team_name)
        if (request.POST.get('reset_all_teams')):
            Branch.reset_all_teams()
            return redirect('central_branch:teams')
    
    #load teams from database
    teams=renderData.Branch.load_teams()
    team_list=[]
    for team in teams:
        team_list.append(team)
            
    context={
        'team':team_list,
        'all_sc_ag':sc_ag,
    }
    return render(request,'Teams/team_homepage.html',context=context)
    


def team_details(request,primary,name):
    
    sc_ag=PortData.get_all_sc_ag(request=request)
    has_access=Branch_View_Access.get_team_details_view_access(request=request)
    '''Detailed panel for the team'''
    current_panel=Branch.load_current_panel()
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

    team_to_update=get_object_or_404(Teams,primary=primary)

    if request.method=='POST':
        if(request.POST.get('add_to_team')):
            #Checking if a button is clicked
            if(request.POST.get('member_select')):
                members_to_add=request.POST.getlist('member_select')
                position=request.POST.get('position')
                #ADDING MEMBER TO TEAM
                for member in members_to_add:
                    if(renderData.Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position)):
                        messages.success(request,"Member Added to the team!")
                    elif(renderData.Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position)==False):
                        messages.error(request,"Member couldn't be added!")
                    elif(renderData.Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position)==DatabaseError):
                        messages.error(request,"An internal Database Error Occured! Please try again!")
                    elif(renderData.Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position) is None):
                        messages.info(request,"You need to make a Panel that is current to add members to Teams!")

                return redirect('central_branch:team_details',primary,name)
            
        if(request.POST.get('remove_member')):
            '''To remove member from team table'''
            try:
                # update members team to None and postion to general member
                Members.objects.filter(ieee_id=request.POST['access_ieee_id']).update(team=None,position=Roles_and_Position.objects.get(id=13)) #ID 13 means general member
                # remove member from the current panel ass well
                Panel_Members.objects.filter(tenure=current_panel.pk,member=request.POST['access_ieee_id']).delete()
                messages.error(request,f"{request.POST['access_ieee_id']} was removed from the Team. The Member was also removed from the current Panel.")
                return redirect('central_branch:team_details',primary,name)
            except Exception as ex:
                messages.error(request,"Something went Wrong!")

        if (request.POST.get('update')):
            '''To update member's position in a team'''
            ieee_id=request.POST.get('access_ieee_id')
            position = request.POST.get('position')
            # update position for member
            Members.objects.filter(ieee_id = ieee_id).update(position = position)
            # update member position in the current panel as well
            Panel_Members.objects.filter(tenure=current_panel.pk,member=ieee_id).update(position=position)
            messages.info(request,"Member Position was updated in the Team and the Current Panel.")
            return redirect('central_branch:team_details',primary,name)
        
        if (request.POST.get('reset_team')):
            '''To remove all members in the team and assigning them as general memeber. Resetting team won't effect the panel'''
            all_memebers_in_team = Members.objects.filter(team = Teams.objects.get(primary=primary))
            all_memebers_in_team.update(team=None,position = Roles_and_Position.objects.get(id=13))
            messages.info(request,"The whole team was reset. Previous Members are preserved in their respective Panel.")
            return redirect('central_branch:team_details',primary,name)

        if(request.POST.get('update_team_details')):
            '''Update Team Details'''
            team_update_form=PortForms.TeamForm(request.POST,request.FILES,instance=team_to_update)
            if(team_update_form.is_valid()):
                team_update_form.save()
                messages.success(request,"Team information was updated!")
                return redirect('central_branch:team_details',primary,name)
    
    else:
        team_update_form=PortForms.TeamForm(instance=team_to_update)

    context={
        'all_sc_ag':sc_ag,
        'team_id':primary,
        'team_name':name,
        'team_members':team_members,
        'positions':positions,
        'insb_members':insb_members,
        'current_panel':current_panel,
        'team_form':team_update_form
        
    }
    if(has_access):
        return render(request,'Teams/team_details.html',context=context)
    else:
        return render(request,"access_denied2.html", { 'all_sc_ag':sc_ag })

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
    
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get all panels from database
    panels = Branch.load_all_panels()
    create_panel_access=Branch_View_Access.get_create_panel_access(request=request)
    if request.method=="POST":
        tenure_year=request.POST['tenure_year']
        current_check=request.POST.get('current_check')
        panel_start_date=request.POST['panel_start_date']
        panel_end_date=request.POST['panel_end_date']
        # create panel
        if(Branch.create_panel(request,tenure_year=tenure_year,current_check=current_check,panel_end_date=panel_end_date,panel_start_date=panel_start_date)):
            return redirect('central_branch:panels')
        
    context={
        'all_sc_ag':sc_ag,
        'panels':panels,
        'create_panel_access':create_panel_access,
    }
    
    return render(request,"Panel/panel_homepage.html",context)


@login_required
def branch_panel_details(request,panel_id):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get panel information
    panel_info = Branch.load_panel_by_id(panel_id)
    # get panel tenure time
    if(panel_info.panel_end_time is None):
        present_date=datetime.now()
        tenure_time=present_date.date()-panel_info.creation_time.date()
    else:
        tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()
    # get all insb members
    all_insb_members=port_render.get_all_registered_members(request)
    
    if(request.method=="POST"):
        # Delete panel
        if(request.POST.get('delete_panel')):
            if(Branch.delete_panel(request,panel_id)):
                return redirect('central_branch:panels')
        
        # Update Panel Settings
        if(request.POST.get('save_changes')):
            panel_tenure=request.POST.get('panel_tenure')
            current_panel_check=request.POST.get('current_panel_check')
            if(current_panel_check is None):
                current_panel_check=False
            else:
                current_panel_check=True
            panel_start_date=request.POST['panel_start_date']
            panel_end_date=request.POST['panel_end_date']
            if(panel_end_date==""):
                panel_end_date=None
            
            if(Branch.update_panel_settings(request=request,panel_tenure=panel_tenure,panel_end_date=panel_end_date,is_current_check=current_panel_check,panel_id=panel_id,panel_start_date=panel_start_date)):
                return redirect('central_branch:panel_details',panel_id)
            else:
                return redirect('central_branch:panel_details',panel_id)
            
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

        
    context={
        'all_sc_ag':sc_ag,
        'panel_id':panel_id,
        'panel_info':panel_info,
        'tenure_time':tenure_time,
        'insb_members':all_insb_members,
        'positions':PortData.get_all_executive_positions_of_branch(request=request,sc_ag_primary=1),#as this is for branch, the primary=1
        'eb_member':PanelMembersData.get_eb_members_from_branch_panel(request=request,panel=panel_id),
    }
    return render(request,'Panel/panel_details.html',context=context)

@login_required
def branch_panel_officers_tab(request,panel_id):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get panel information
    panel_info = Branch.load_panel_by_id(panel_id)
     # get panel tenure time
    if(panel_info.panel_end_time is None):
        present_date=datetime.now()
        tenure_time=present_date.date()-panel_info.creation_time.date()
    else:
        tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()
    # get all insb members
    all_insb_members=port_render.get_all_registered_members(request)
    
    if(request.method=="POST"):
        # Check whether the add officer button was pressed
        if(request.POST.get('add_officer_to_panel')):
            # get position
            position=request.POST.get('position1')
            # get team
            team=request.POST.get('team')
            # get members as a list
            members=request.POST.getlist('member_select1')

            if(PanelMembersData.add_members_to_branch_panel(request=request,members=members,panel_info=panel_info,position=position,team_primary=team)):
                return redirect('central_branch:panel_details_officers',panel_id)
        
        # Check whether the update button was pressed
        if(request.POST.get('remove_member_officer')):
            # get ieee_id of the member
            ieee_id=request.POST['remove_officer_member']
            # remove member
            if(PanelMembersData.remove_member_from_panel(request=request,ieee_id=ieee_id,panel_id=panel_info.pk)):
                return redirect('central_branch:panel_details_officers',panel_id)

    
    context={
        'all_sc_ag':sc_ag,
        'panel_id':panel_id,
        'panel_info':panel_info,
        'tenure_time':tenure_time,
        'officer_member':PanelMembersData.get_officer_members_from_branch_panel(panel=panel_id,request=request),
        'insb_members':all_insb_members,
        'officer_positions':PortData.get_all_officer_positions_with_sc_ag_id(request=request,sc_ag_primary=1),#as this is for branch, the primary=1
        'teams':PortData.get_teams_of_sc_ag_with_id(request,sc_ag_primary=1),
    }
    return render(request,'Panel/officer_members_tab.html',context=context)

@login_required
def branch_panel_volunteers_tab(request,panel_id):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get panel information
    panel_info = Branch.load_panel_by_id(panel_id)
     # get panel tenure time
    if(panel_info.panel_end_time is None):
        present_date=datetime.now()
        tenure_time=present_date.date()-panel_info.creation_time.date()
    else:
        tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()
    
    # get all insb members
    all_insb_members=port_render.get_all_registered_members(request)
    
    if(request.method=="POST"):
        # check whether the add buton was pressed
        if(request.POST.get('add_volunteer_to_panel')):
            # get_position
            position=request.POST.get('position2')
            # get team
            team=request.POST.get('team1')
            # get members as a list
            members=request.POST.getlist('member_select2')

            if(PanelMembersData.add_members_to_branch_panel(request=request,members=members,panel_info=panel_info,position=position,team_primary=team)):
                return redirect('central_branch:panel_details_volunteers',panel_id)
        # check whether the remove button was pressed
        if(request.POST.get('remove_member_volunteer')):
            # get ieee id of the member
            ieee_id=request.POST['remove_officer_member']
            # remove member
            if(PanelMembersData.remove_member_from_panel(request=request,ieee_id=ieee_id,panel_id=panel_info.pk)):
                return redirect('central_branch:panel_details_volunteers',panel_id)

    
    
    context={
        'all_sc_ag':sc_ag,
        'panel_id':panel_id,
        'panel_info':panel_info,
        'tenure_time':tenure_time,
        'insb_members':all_insb_members,
        'all_insb_volunteer_positions':PortData.get_all_volunteer_position_with_sc_ag_id(request,sc_ag_primary=1),
        'volunteer_positions':PortData.get_all_volunteer_position_with_sc_ag_id(request=request,sc_ag_primary=1),
        'teams':PortData.get_teams_of_sc_ag_with_id(request,sc_ag_primary=1),
        'volunteer_members':PanelMembersData.get_volunteer_members_from_branch_panel(request=request,panel=panel_id),
    }
    return render(request,'Panel/volunteer_members_tab.html',context=context)

@login_required
def branch_panel_alumni_tab(request,panel_id):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get panel information
    panel_info = Branch.load_panel_by_id(panel_id)
     # get panel tenure time
    if(panel_info.panel_end_time is None):
        present_date=datetime.now()
        tenure_time=present_date.date()-panel_info.creation_time.date()
    else:
        tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()
    
    if(request.method=="POST"):
        # Create New Alumni Member
        if(request.POST.get('create_new_alumni')):
            try:
                alumni_name=request.POST['alumni_name']
                alumni_email=request.POST['alumni_email']
                alumni_contact_no=request.POST['alumni_contact_no']
                alumni_facebook_link=request.POST['alumni_facebook_link']
                alumni_linkedin_link=request.POST['alumni_linkedin_link']
                alumni_picture=request.FILES.get('alumni_picture') 

            except MultiValueDictKeyError:
                messages.error(request,"Image can not be uploaded!")
            finally:
                # create alumni
                if(Alumnis.create_alumni_members(
                    request=request,contact_no=alumni_contact_no,
                    email=alumni_email,
                    facebook_link=alumni_facebook_link,
                    linkedin_link=alumni_linkedin_link,
                    name=alumni_name,
                    picture=alumni_picture)):
                    return redirect('central_branch:panel_details_alumni',panel_id)
                else:
                    messages.error(request,'Failed to Add new alumni!')
        
        # Add alumni to panel
        if(request.POST.get('add_alumni_to_panel')):
            alumni_to_add=request.POST['alumni_select']
            position=request.POST['alumni_position']
            
            for i in alumni_to_add:            
                if(PanelMembersData.add_alumns_to_branch_panel(request=request,alumni_id=alumni_to_add,panel_id=panel_id,position=position)):
                    pass
            return redirect('central_branch:panel_details_alumni',panel_id)
        
        if(request.POST.get('remove_member_alumni')):
            alumni_to_remove=request.POST['remove_alumni_member']
            if(PanelMembersData.remove_alumns_from_branch_panel(request=request,member_to_remove=alumni_to_remove,panel_id=panel_id)):
                return redirect('central_branch:panel_details_alumni',panel_id)
    
    context={
        'all_sc_ag':sc_ag,
        'panel_id':panel_id,
        'panel_info':panel_info,
        'tenure_time':tenure_time,
        'alumni_members':Alumnis.getAllAlumns(),
        'positions':PortData.get_all_executive_positions_of_branch(request=request,sc_ag_primary=1),#as this is for branch, the primary=1
        'alumni_members_in_panel':PanelMembersData.get_alumni_members_from_panel(panel=panel_id,request=request)
    }
    return render(request,'Panel/alumni_members_tab.html',context=context)



@login_required
def others(request):
    return render(request,"others.html")

@login_required
def manage_research(request):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # load all research papers
    researches = Research_Papers.objects.filter(is_requested=False).order_by('-publish_date','publish_research')
    '''function for adding new Research paper'''
    if request.method == "POST":
        add_research_form=ResearchPaperForm(request.POST,request.FILES)
        add_research_category_form=ResearchCategoryForm(request.POST)

        if(request.POST.get('add_research')):
            if(add_research_form.is_valid()):
                add_research_form.save()
                messages.success(request,"A new Research Paper was added!")
                return redirect('central_branch:manage_research')
        if(request.POST.get('add_research_category')):
            if(add_research_category_form.is_valid()):
                add_research_category_form.save()
                messages.success(request,"A new Research Category was added!")
                return redirect('central_branch:manage_research')
        if(request.POST.get('remove_research')):
            MainWebsiteRenderData.delete_research_paper(request=request)
            return redirect('central_branch:manage_research')
    else:
        form=ResearchPaperForm
        form2=ResearchCategoryForm
    context={
        'all_sc_ag':sc_ag,
        'form':form,
        'form2':form2,'all_researches':researches,
    }
    return render(request,"Manage Website/Publications/Research Paper/manage_research_paper.html",context=context)

@login_required
def manage_research_request(request):
    # get all research requests
    research_requests=Research_Papers.objects.filter(is_requested=True).order_by('-publish_date')
    if(request.method=="POST"):
        if(request.POST.get('remove_research')):
            MainWebsiteRenderData.delete_research_paper(request=request)
            return redirect('central_branch:manage_research_request')
    context={
        'all_research_requests':research_requests
    }
    return render(request,"Manage Website/Publications/Research Paper/manage_paper_request.html",context=context)

@login_required
def publish_research_request(request,pk):
    # get research to publish
    research_to_publish=get_object_or_404(Research_Papers,pk=pk)
    if(request.method=="POST"):
        research_form=ResearchPaperForm(request.POST,request.FILES,instance=research_to_publish)
        if(request.POST.get('publish_research')):
            if(research_form.is_valid()):
                research_to_publish.is_requested=False
                research_to_publish.publish_research=True
                research_to_publish.save()
                research_form.save()
                messages.success(request,f"{research_to_publish.title} was Published in the Main Website")
                return redirect('central_branch:manage_research_request')
    else:
        research_form=ResearchPaperForm(instance=research_to_publish)            
    context={
        'research':research_to_publish,
        'form':research_form,
    }
    return render(request,"Manage Website/Publications/Research Paper/publish_research.html",context=context)

@login_required
def update_researches(request,pk):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get the research and Form
    research_to_update=get_object_or_404(Research_Papers,pk=pk)
    if(request.method=="POST"):
        if(request.POST.get('update_research_paper')):
            form=ResearchPaperForm(request.POST,request.FILES,instance=research_to_update)
            if(form.is_valid()):
                form.save()
                messages.info(request,"Research Paper Informations were updated")
                return redirect('central_branch:manage_research')
    else:
        form=ResearchPaperForm(instance=research_to_update)
    
    context={
        'all_sc_ag':sc_ag,
        'form':form,
        'research_paper':research_to_update,
    }
    return render(request,"Manage Website/Publications/Research Paper/update_research_papers.html",context=context)

@login_required
def manage_blogs(request):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # Load all blogs
    all_blogs=Blog.objects.filter(is_requested=False)
    
    form=BlogsForm
    form2=BlogCategoryForm
    
    if(request.method=="POST"):
        form=BlogsForm(request.POST,request.FILES)
        if(request.POST.get('add_blog')):
            if(form.is_valid()):
                form.save()
                messages.success(request,"A new Blog was added!")
                return redirect('central_branch:manage_blogs')
        
        if(request.POST.get('add_blog_category')):
            form2=BlogCategoryForm(request.POST)
            if(form2.is_valid()):
                form2.save()
                messages.success(request,"A new Blog Category was added!")
                return redirect('central_branch:manage_blogs')
        if(request.POST.get('remove_blog')):
            MainWebsiteRenderData.delete_blog(request=request)
            return redirect('central_branch:manage_blogs')

    context={
        'all_sc_ag':sc_ag,
        # get form
        'form':form,
        'form2':form2,
        'all_blogs':all_blogs,
        
    }
    
    return render(request,"Manage Website/Publications/Blogs/manage_blogs.html",context=context)

@login_required
def update_blogs(request,pk):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get the blog and form
    blog_to_update=get_object_or_404(Blog,pk=pk)
    if(request.method=="POST"):
        if(request.POST.get('update_blog')):
            form=BlogsForm(request.POST,request.FILES,instance=blog_to_update)
            if(form.is_valid()):
                form.save()
                messages.info(request,"Blog Informations were updated")
                return redirect('central_branch:manage_blogs')
    else:
        form=BlogsForm(instance=blog_to_update)
    
    context={
        'all_sc_ag':sc_ag,
        'form':form,
        'blog':blog_to_update,
    }

    return render(request,"Manage Website/Publications/Blogs/update_blogs.html",context=context)

@login_required
def blog_requests(request):
    # get all blog requests
    all_requested_blogs=Blog.objects.filter(is_requested=True).order_by('-date')
    
    if(request.method=="POST"):
        if(request.POST.get('remove_blog')):
            get_blog_to_remove=Blog.objects.get(pk=request.POST['blog_pk'])
            # delete blog banner picture from system at first
            if(os.path.isfile(get_blog_to_remove.blog_banner_picture.path)):
                os.remove(get_blog_to_remove.blog_banner_picture.path)
            # remove the requested blog object from database
            get_blog_to_remove.delete()
            messages.warning(request,"The blog was deleted from requests!")
            return redirect('central_branch:blog_requests')
    
    context={
        'all_requested_blogs':all_requested_blogs
    }
    return render(request,"Manage Website/Publications/Blogs/blog_requests.html",context=context)

@login_required
def publish_blog_request(request,pk):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get the blog and form
    blog_to_publish=get_object_or_404(Blog,pk=pk)
    if(request.method=="POST"):
        if(request.POST.get('publish_blog')):
            form=BlogsForm(request.POST,request.FILES,instance=blog_to_publish)
            if(form.is_valid()):
                form.save()
                blog_to_publish.is_requested=False
                blog_to_publish.publish_blog=True
                blog_to_publish.save()
                print("Saved")
                print(blog_to_publish.publish_blog)
                messages.info(request,"Blog was published in the main website")
                return redirect('central_branch:blog_requests')
    else:
        form=BlogsForm(instance=blog_to_publish)
    
    context={
        'all_sc_ag':sc_ag,
        'form':form,
        'blog':blog_to_publish,
    }
    return render(request,"Manage Website/Publications/Blogs/publish_blog.html",context=context)

from main_website.models import HomePageTopBanner
@login_required
def manage_website_homepage(request):
    sc_ag=PortData.get_all_sc_ag(request=request)

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
                    first_layer_text_colored=request.POST['first_layer_text_colored'],
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
        'all_sc_ag':sc_ag,
        'user_data':user_data,
        'topBannerItems':topBannerItems,
        'bannerPictureWithNumbers':existing_banner_picture_with_numbers,
        'media_url':settings.MEDIA_URL
    }
    return render(request,'Manage Website/Homepage/manage_web_homepage.html',context)



@login_required
def manage_about(request):

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)

        about_ieee, created = About_IEEE.objects.get_or_create(id=1)
        page_title = 'about_ieee'

        if request.method == "POST":
            if 'save' in request.POST:
                about_details = request.POST['about_details']
                learn_more_link = request.POST['learn_more_link']
                mission_and_vision_link = request.POST['mission_and_vision_link']
                community_details = request.POST['community_details']
                start_with_ieee_details = request.POST['start_with_ieee_details']
                collaboration_details = request.POST['collaboration_details']
                publications_details = request.POST['publications_details']
                events_and_conferences_details = request.POST['events_and_conferences_details']
                achievements_details = request.POST['achievements_details']
                innovations_and_developments_details = request.POST['innovations_and_developments_details']
                students_and_member_activities_details = request.POST['students_and_member_activities_details']
                quality_details = request.POST['quality_details']
                join_now_link = request.POST['join_now_link']
                asia_pacific_link = request.POST['asia_pacific_link']
                ieee_computer_organization_link = request.POST['ieee_computer_organization_link']
                customer_service_number = request.POST['customer_service_number']
                presidents_names = request.POST['presidents_names']
                founders_names = request.POST['founders_names']
                
                about_image = request.FILES.get('about_picture')
                community_image = request.FILES.get('community_picture')
                innovations_and_developments_image = request.FILES.get('innovations_and_developments_picture')
                students_and_member_activities_image = request.FILES.get('students_and_member_activities_picture')
                quality_image = request.FILES.get('quality_picture')

                if about_image == None:
                    about_image = about_ieee.about_image
                if community_image == None:
                    community_image = about_ieee.community_image
                if innovations_and_developments_image == None:
                    innovations_and_developments_image = about_ieee.innovations_and_developments_image
                if students_and_member_activities_image == None:
                    students_and_member_activities_image = about_ieee.students_and_member_activities_image
                if quality_image == None:
                    quality_image = about_ieee.quality_image

                if(Branch.set_about_ieee_page(about_details, learn_more_link, mission_and_vision_link, community_details, start_with_ieee_details, collaboration_details,
                                        publications_details, events_and_conferences_details, achievements_details, innovations_and_developments_details,
                                        students_and_member_activities_details, quality_details, join_now_link, asia_pacific_link, ieee_computer_organization_link,
                                        customer_service_number, presidents_names, founders_names, about_image, community_image,
                                        innovations_and_developments_image, students_and_member_activities_image, quality_image)):
                    messages.success(request, "Details Updated Successfully!")
                else:
                    messages.error(request, "Something went wrong while updating the details!")
                
                return redirect('central_branch:manage_about')
            elif 'remove' in request.POST:
                image = request.POST.get('image_delete')
                image_id = request.POST.get('image_id')
                if Branch.about_ieee_delete_image(image_id,image):
                    messages.success(request,"Deleted Successfully!")
                else:
                    messages.error(request,"Error while deleting picture.")
                return redirect("central_branch:manage_about")
            elif 'add_link' in request.POST:
                category = request.POST.get('link_category')
                title = request.POST.get('title')
                link = request.POST.get('form_link_add')

                if(Branch.add_about_page_link(page_title, category, title, link)):
                    messages.success(request, 'Link added successfully')
                else:
                    messages.error(request,'Something went wrong while adding the link')

                return redirect("central_branch:manage_about")
            elif 'update_link' in request.POST:
                link_id = request.POST.get('link_id')
                title = request.POST.get('title')
                link = request.POST.get('form_link_edit')

                if(Branch.update_about_page_link(link_id, page_title, title, link)):
                    messages.success(request,'Link updated successfully')
                else:
                    messages.error(request,'Something went wrong while updating the link')
                
                return redirect("central_branch:manage_about")
            elif 'remove_form_link' in request.POST:
                link_id = request.POST.get('link_id')

                if(Branch.remove_about_page_link(link_id, page_title)):
                    messages.success(request,'Link removed successfully')
                else:
                    messages.error(request,'Something went wrong while deleting the link')

                return redirect("central_branch:manage_about")

        page_links = Branch.get_about_page_links(page_title=page_title)
        
        context={
            'all_sc_ag':sc_ag,
            'about_ieee':about_ieee,
            'media_url':settings.MEDIA_URL,
            'page_links':page_links
        }
        return render(request,'Manage Website/About/About IEEE/manage_ieee.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")


@login_required
def ieee_region_10(request):
    sc_ag=PortData.get_all_sc_ag(request=request)

    about_ieee_region_10, created = IEEE_Region_10.objects.get_or_create(id=1)
    page_title = 'ieee_region_10'

    if request.method == 'POST':
        if 'save' in request.POST:
            ieee_region_10_description = request.POST['ieee_region_10_details']
            ieee_region_10_history_link = request.POST['region_10_history_link']
            young_professionals_description = request.POST['young_professionals_details']
            women_in_engineering_ddescription = request.POST['women_in_engineering_details']
            student_and_member_activities_description = request.POST['student_and_member_activities_details']
            educational_activities_and_involvements_description = request.POST['educational_activities_and_involvements_details']
            industry_relations_description = request.POST['industry_relations_details']
            membership_development_description = request.POST['membership_development_details']
            events_and_conference_description = request.POST['events_and_conference_details']
            home_page_link = request.POST['home_page_link']
            website_link = request.POST['website_link']
            membership_inquiry_link = request.POST['membership_inquiry_link']
            for_volunteers_link = request.POST['for_volunteers_link']
            contact_number = request.POST['contact_number']

            ieee_region_10_image = request.FILES.get('ieee_region_10_picture')
            young_professionals_image = request.FILES.get('young_professionals_picture')
            membership_development_image = request.FILES.get('membership_development_picture')
            background_picture_parallax = request.FILES.get('background_picture')
            events_and_conference_image = request.FILES.get('events_and_conference_picture')

            if ieee_region_10_image == None:
                ieee_region_10_image = about_ieee_region_10.ieee_region_10_image
            if young_professionals_image == None:
                young_professionals_image = about_ieee_region_10.young_professionals_image
            if membership_development_image == None:
                membership_development_image = about_ieee_region_10.membership_development_image
            if background_picture_parallax == None:
                background_picture_parallax = about_ieee_region_10.background_picture_parallax
            if events_and_conference_image == None:
                events_and_conference_image = about_ieee_region_10.events_and_conference_image

            if(Branch.set_ieee_region_10_page(ieee_region_10_description,ieee_region_10_history_link,young_professionals_description,women_in_engineering_ddescription,
                                              student_and_member_activities_description,educational_activities_and_involvements_description,industry_relations_description,
                                              membership_development_description,events_and_conference_description,home_page_link,website_link,membership_inquiry_link,
                                              for_volunteers_link,contact_number,ieee_region_10_image,young_professionals_image,membership_development_image,
                                              background_picture_parallax,events_and_conference_image)):
                messages.success(request, "Details Updated Successfully!")
            else:
                messages.error(request, "Something went wrong while updating the details!")
            
            return redirect('central_branch:ieee_region_10')
        elif 'remove' in request.POST:
            image = request.POST.get('image_delete')
            image_id = request.POST.get('image_id')
            if Branch.ieee_region_10_page_delete_image(image_id,image):
                messages.success(request,"Deleted Successfully!")
            else:
                messages.error(request,"Error while deleting picture.")
            return redirect("central_branch:ieee_region_10")
        elif 'add_link' in request.POST:
            category = request.POST.get('link_category')
            title = request.POST.get('title')
            link = request.POST.get('form_link_add')

            if(Branch.add_about_page_link(page_title, category, title, link)):
                messages.success(request, 'Link added successfully')
            else:
                messages.error(request,'Something went wrong while adding the link')

            return redirect("central_branch:ieee_region_10")
        elif 'update_link' in request.POST:
            link_id = request.POST.get('link_id')
            title = request.POST.get('title')
            link = request.POST.get('form_link_edit')

            if(Branch.update_about_page_link(link_id, page_title, title, link)):
                messages.success(request,'Link updated successfully')
            else:
                messages.error(request,'Something went wrong while updating the link')
            
            return redirect("central_branch:ieee_region_10")
        elif 'remove_form_link' in request.POST:
            link_id = request.POST.get('link_id')

            if(Branch.remove_about_page_link(link_id, page_title)):
                messages.success(request,'Link removed successfully')
            else:
                messages.error(request,'Something went wrong while deleting the link')

            return redirect("central_branch:ieee_region_10")
        
    page_links = Branch.get_about_page_links(page_title=page_title)

    context={
        'all_sc_ag':sc_ag,
        'ieee_region_10':about_ieee_region_10,
        'media_url':settings.MEDIA_URL,
        'page_links':page_links
    }
    return render(request,'Manage Website/About/IEEE Region 10/ieee_region_10.html',context=context)


@login_required
def ieee_bangladesh_section(request):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)

        ieee_bangladesh_section, created = IEEE_Bangladesh_Section.objects.get_or_create(id=1)
        page_title = 'ieee_bangladesh_section'

        if request.method == 'POST':
            if 'save' in request.POST:
                about_details = request.POST['about_details']
                ieeebd_link = request.POST['ieeebd_link']
                members_and_volunteers_details = request.POST['members_and_volunteers_details']
                benefits_details = request.POST['benefits_details']
                student_branches_details = request.POST['student_branches_details']
                affinity_groups_details = request.POST['affinity_groups_details']
                communty_and_society_details = request.POST['communty_and_society_details']
                achievements_details = request.POST['achievements_details']
                chair_name = request.POST['chair_name']
                chair_email = request.POST['chair_email']
                secretary_name = request.POST['secretary_name']
                secretary_email = request.POST['secretary_email']
                office_secretary_name = request.POST['office_secretary_name']
                office_secretary_number = request.POST['office_secretary_number']

                about_image = request.FILES.get('about_image')
                members_and_volunteers_image = request.FILES.get('members_and_volunteers_image')

                if about_image == None:
                        about_image = ieee_bangladesh_section.ieee_bangladesh_logo
                if members_and_volunteers_image == None:
                    members_and_volunteers_image = ieee_bangladesh_section.member_and_volunteer_picture

                if(Branch.set_ieee_bangladesh_section_page(about_details, ieeebd_link, members_and_volunteers_details, benefits_details,
                                                        student_branches_details, affinity_groups_details, communty_and_society_details,
                                                        achievements_details, chair_name, chair_email, secretary_name,
                                                        secretary_email, office_secretary_name, office_secretary_number, about_image, members_and_volunteers_image)):
                    messages.success(request, "Details Updated Successfully!")
                else:
                    messages.error(request, "Something went wrong while updating the details!")

                return redirect('central_branch:ieee_bangladesh_section')
            elif 'remove' in request.POST:
                image = request.POST.get('image_delete')
                image_id = request.POST.get('image_id')
                if Branch.ieee_bangladesh_section_page_delete_image(image_id,image):
                    messages.success(request,"Deleted Successfully!")
                else:
                    messages.error(request,"Error while deleting picture.")
                return redirect("central_branch:ieee_bangladesh_section")
            elif 'add_link' in request.POST:
                category = request.POST.get('link_category')
                title = request.POST.get('title')
                link = request.POST.get('form_link_add')

                if(Branch.add_about_page_link(page_title, category, title, link)):
                    messages.success(request, 'Link added successfully')
                else:
                    messages.error(request,'Something went wrong while adding the link')

                return redirect("central_branch:ieee_bangladesh_section")
            elif 'update_link' in request.POST:
                link_id = request.POST.get('link_id')
                title = request.POST.get('title')
                link = request.POST.get('form_link_edit')

                if(Branch.update_about_page_link(link_id, page_title, title, link)):
                    messages.success(request,'Link updated successfully')
                else:
                    messages.error(request,'Something went wrong while updating the link')
                
                return redirect("central_branch:ieee_bangladesh_section")
            elif 'remove_form_link' in request.POST:
                link_id = request.POST.get('link_id')

                if(Branch.remove_about_page_link(link_id, page_title)):
                    messages.success(request,'Link removed successfully')
                else:
                    messages.error(request,'Something went wrong while deleting the link')

                return redirect("central_branch:ieee_bangladesh_section")
            
        page_links = Branch.get_about_page_links(page_title=page_title)

        context={
            'all_sc_ag':sc_ag,
            'ieee_bangladesh_section':ieee_bangladesh_section,
            'page_links':page_links,
            'media_url':settings.MEDIA_URL,
        }
        return render(request,'Manage Website/About/IEEE Bangladesh Section/ieee_bangladesh_section.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def ieee_nsu_student_branch(request):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)

        ieee_nsu_student_branch, created = IEEE_NSU_Student_Branch.objects.get_or_create(id=1)

        if request.method == 'POST':
            if 'save' in request.POST:
                about_nsu_student_branch = request.POST['about_details']
                chapters_description = request.POST['chapters_details']
                ras_read_more_link = request.POST['ras_read_more_link']
                pes_read_more_link = request.POST['pes_read_more_link']
                ias_read_more_link = request.POST['ias_read_more_link']
                wie_read_more_link = request.POST['wie_read_more_link']
                creative_team_description = request.POST['creative_team_details']
                mission_description = request.POST['mission_details']
                vision_description = request.POST['vision_details']
                events_description = request.POST['events_details']
                join_now_link = request.POST['join_now_link']
                achievements_description = request.POST['achievements_details']

                about_image = request.FILES.get('about_image')
                ras_image = request.FILES.get('ras_image')
                pes_image = request.FILES.get('pes_image')
                ias_image = request.FILES.get('ias_image')
                wie_image = request.FILES.get('wie_image')
                mission_image = request.FILES.get('mission_image')
                vision_image = request.FILES.get('vision_image')

                if about_image == None:
                    about_image = ieee_nsu_student_branch.about_image
                if ras_image == None:
                    ras_image = ieee_nsu_student_branch.ras_image
                if pes_image == None:
                    pes_image = ieee_nsu_student_branch.pes_image
                if ias_image == None:
                    ias_image = ieee_nsu_student_branch.ias_image
                if wie_image == None:
                    wie_image = ieee_nsu_student_branch.wie_image
                if mission_image == None:
                    mission_image = ieee_nsu_student_branch.mission_image
                if vision_image == None:
                    vision_image = ieee_nsu_student_branch.vision_image
                
                if(Branch.set_ieee_nsu_student_branch_page(about_nsu_student_branch, chapters_description, ras_read_more_link,
                                                        pes_read_more_link, ias_read_more_link, wie_read_more_link, creative_team_description,
                                                        mission_description, vision_description, events_description, join_now_link, achievements_description,
                                                        about_image,ras_image,pes_image,ias_image,wie_image,mission_image,vision_image)):
                    messages.success(request, "Details Updated Successfully!")
                else:
                    messages.error(request, "Something went wrong while updating the details!")

                return redirect('central_branch:ieee_nsu_student_branch')
            elif 'remove' in request.POST:
                image = request.POST.get('image_delete')
                image_id = request.POST.get('image_id')
                if Branch.ieee_nsu_student_branch_page_delete_image(image_id,image):
                    messages.success(request,"Deleted Successfully!")
                else:
                    messages.error(request,"Error while deleting picture.")
                return redirect("central_branch:ieee_nsu_student_branch")

        context={
            'all_sc_ag':sc_ag,
            'ieee_nsu_student_branch':ieee_nsu_student_branch,
            'media_url':settings.MEDIA_URL,
        }
        return render(request,'Manage Website/About/IEEE NSU Student Branch/ieee_nsu_student_branch.html', context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def faq(request):

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)


        if request.method == "POST":
            #when user submits a new category title
            if request.POST.get('add_category'):
                #getting the new title for the category
                category_title = request.POST.get('category_title')
            
            if request.POST.get('update_faq'):

                questions = request.POST.getlist('faq_question')
                answers = request.POST.getlist('faq_question_answer')

                print(questions)
                print(answers)
                


        context={
            'all_sc_ag':sc_ag,
        }
        return render(request,'Manage Website/About/FAQ/portal_faq.html', context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")



@login_required
def manage_achievements(request):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # load the achievement form
    form=AchievementForm
    # load all SC AG And Branch
    load_award_of=Chapters_Society_and_Affinity_Groups.objects.all().order_by('primary')
    
    # load all achievements
    all_achievements=MainWebsiteRenderData.get_all_achievements(request=request)
    
    if(request.method=="POST"):
        if(request.POST.get('add_achievement')):
            # add award
            if(MainWebsiteRenderData.add_awards(request=request)):
                return redirect('central_branch:manage_achievements')
            else:
                return redirect('central_branch:manage_achievements')
        if(request.POST.get('remove_achievement')):
            if(MainWebsiteRenderData.delete_achievement(request=request)):
                return redirect('central_branch:manage_achievements')
            else:
                return redirect('central_branch:manage_achievements')

    context={
        'all_sc_ag':sc_ag,
        'form':form,
        'load_all_sc_ag':load_award_of,
        'all_achievements':all_achievements,
    }
    return render(request,'Manage Website/Activities/manage_achievements.html',context=context)

@login_required
def update_achievements(request,pk):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get the achievement and form
    achievement_to_update=get_object_or_404(Achievements,pk=pk)
    if(request.method=="POST"):
        if(request.POST.get('update_achievement')):
            form=AchievementForm(request.POST,request.FILES,instance=achievement_to_update)
            if(form.is_valid()):
                form.save()
                messages.info(request,"Achievement Informations were updates")
                return redirect('central_branch:manage_achievements')
    else:
        form=AchievementForm(instance=achievement_to_update)
    
    context={
        'all_sc_ag':sc_ag,
        'form':form,
        'achievement':achievement_to_update,
    }

    return render(request,"Manage Website/Activities/achievements_update_section.html",context=context)

@login_required
def manage_news(request):
    sc_ag=PortData.get_all_sc_ag(request=request)

    form=NewsForm
    get_all_news=News.objects.all().order_by('-news_date')
    
    if(request.method=="POST"):
        if(request.POST.get('add_news')):
            form=NewsForm(request.POST,request.FILES)
            if(form.is_valid()):
                form.save()
                messages.success(request,"A new News was added to the main page")
                return redirect('central_branch:manage_news')
        if(request.POST.get('remove_news')):
            news_to_delete=request.POST['remove_news']
            news_obj=News.objects.get(pk=news_to_delete)
            if(os.path.isfile(news_obj.news_picture.path)):
                os.remove(news_obj.news_picture.path)
            news_obj.delete()
            messages.info(request,"A news item was deleted!")
            return redirect('central_branch:manage_news')
    
    context={
        'all_sc_ag':sc_ag,
        'form':form,
        'all_news':get_all_news
    }
    return render(request,"Manage Website/Activities/manage_news.html",context=context)

@login_required
def update_news(request,pk):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get the news instance to update
    news_to_update = get_object_or_404(News, pk=pk)
    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES, instance=news_to_update)
        if form.is_valid():
            form.save()
            messages.info(request,"News Informations were updates")
            return redirect('central_branch:manage_news')
    else:
        form = NewsForm(instance=news_to_update)
    context={
        'all_sc_ag':sc_ag,
        'form':form,
        'news':news_to_update,
    }
    return render(request,'Manage Website/Activities/news_update_section.html',context=context)


@login_required
def manage_magazines(request):
    # get form
    magazine_form = MagazineForm
    
    # get all magazines
    all_magazines=Magazines.objects.all().order_by('-publish_date')
    if(request.method=="POST"):
        magazine_form=MagazineForm(request.POST,request.FILES)
        if(request.POST.get('add_magazine')):
            if (magazine_form.is_valid()):
                magazine_form.save()
                messages.success(request,"New Magazine Added Successfully")
                return redirect('central_branch:manage_magazines')
        if(request.POST.get('remove_magazine')):
            magazine_to_delete=request.POST['magazine_pk']
            get_magazine=Magazines.objects.get(pk=magazine_to_delete)
            if(os.path.isfile(get_magazine.magazine_picture.path)):
                os.remove(get_magazine.magazine_picture.path)
            if(os.path.isfile(get_magazine.magazine_file.path)):
                os.remove(get_magazine.magazine_file.path)
            get_magazine.delete()
            messages.warning(request,"One Item Deleted from Magazines")
            return redirect('central_branch:manage_magazines')
            
                    
    context={
        'magazine_form':magazine_form,
        'all_magazines':all_magazines,
    }
    return render(request,'Manage Website/Publications/Magazine/manage_magazine.html',context=context)


@login_required
def update_magazine(request,pk):
    # get the magazine to update
    magazine_to_update=get_object_or_404(Magazines,pk=pk)
    
    if request.method == "POST":
        update_form = MagazineForm(request.POST, request.FILES, instance=magazine_to_update)
        if update_form.is_valid():
            update_form.save()
            messages.info(request,"Magazine Informations were updated")
            return redirect('central_branch:manage_magazines')
    else:
        update_form = MagazineForm(instance=magazine_to_update)
    context={
        'update_form':update_form,
        'magazine':magazine_to_update,
    }
    
    return render(request,'Manage Website/Publications/Magazine/update_magazine.html',context=context)

@login_required
def manage_gallery(request):
    
    # get all images of gallery
    all_images = GalleryImages.objects.all().order_by('-pk')
    all_videos=GalleryVideos.objects.all().order_by('-pk')
    
    if(request.method=="POST"):
        image_form=GalleryImageForm(request.POST,request.FILES)
        video_form=GalleryVideoForm(request.POST)
        if(request.POST.get('add_image')):
            if(image_form.is_valid()):
                image_form.save()
                messages.success(request,"New Image added Successfully!")
                return redirect('central_branch:manage_gallery')
        if(request.POST.get('remove_image')):
            image_to_delete=GalleryImages.objects.get(pk=request.POST['image_pk'])
            # first delete the image from filesystem
            if(os.path.isfile(image_to_delete.image.path)):
                os.remove(image_to_delete.image.path)
            image_to_delete.delete()
            messages.warning(request,"An Image from the Gallery was deleted!")
            return redirect('central_branch:manage_gallery')

        if(request.POST.get('add_video')):
            if(video_form.is_valid()):
                video_form.save()
                messages.success(request,"New Video added Successfully")
                return redirect('central_branch:manage_gallery')
        if(request.POST.get('remove_video')):
            video_to_delete=GalleryVideos.objects.get(pk=request.POST['video_pk'])
            video_to_delete.delete()
            messages.success(request,"A Video from the Gallery was deleted!")
            return redirect('central_branch:manage_gallery')
        
    context={
        'image_form':GalleryImageForm,
        'video_form':GalleryVideoForm,
        'all_images':all_images,
        'all_videos':all_videos,
    }
    
    return render(request,'Manage Website/Publications/Gallery/manage_gallery.html',context=context)

@login_required
def update_images(request,pk):
     # get the magazine to update
    image_to_update=get_object_or_404(GalleryImages,pk=pk)
    
    if request.method == "POST":
        if(request.POST.get('update_image')):
            update_form = GalleryImageForm(request.POST, request.FILES, instance=image_to_update)
            if update_form.is_valid():
                update_form.save()
                messages.info(request,"Image was updated")
                return redirect('central_branch:manage_gallery')
    else:
        update_form = GalleryImageForm(instance=image_to_update)
    context={
        'update_form':update_form,
        'image':image_to_update,
    }
    return render(request,"Manage Website/Publications/Gallery/update_images.html",context=context)

@login_required
def update_videos(request,pk):
     # get the magazine to update
    video_to_update=get_object_or_404(GalleryVideos,pk=pk)
    
    if request.method == "POST":
        if(request.POST.get('update_video')):
            update_form = GalleryVideoForm(request.POST, instance=video_to_update)
            if update_form.is_valid():
                update_form.save()
                messages.info(request,"Video was updated")
                return redirect('central_branch:manage_gallery')
    else:
        update_form = GalleryVideoForm(instance=video_to_update)
    context={
        'update_form':update_form,
        'video':video_to_update,
    }
    return render(request,"Manage Website/Publications/Gallery/update_videos.html",context=context)

@login_required
def manage_exemplary_members(request):
    # get all exemplary members
    exemplary_members = ExemplaryMembers.objects.all().order_by('rank')
    
    if(request.method=="POST"):
        exemplary_member_form=ExemplaryMembersForm(request.POST,request.FILES)
        if(request.POST.get('add_member')):
            if(exemplary_member_form.is_valid()):
                exemplary_member_form.save()
                messages.success(request,f"{request.POST['member_name']} was added to Exemplary Members")
                return redirect('central_branch:manage_exemplary_members')
        if(request.POST.get('remove_member')):
            member_to_delete=ExemplaryMembers.objects.get(pk=request.POST['remove_member_pk'])
            # delete image of the member
            if(os.path.isfile(member_to_delete.member_picture.path)):
                os.remove(member_to_delete.member_picture.path)
            messages.warning(request,f"Member {member_to_delete.member_name} was deleted!")
            member_to_delete.delete()
            return redirect('central_branch:manage_exemplary_members')
        
    context={
        'all_exemplary_members':exemplary_members,
        'exemplary_member_form':ExemplaryMembersForm,
    }
    return render(request,"Manage Website/Exemplary Members/exemplary_member.html",context=context)

@login_required
def update_exemplary_members(request,pk):
    # get memeber to update
    member_to_update=ExemplaryMembers.objects.get(pk=pk)
    if request.method=='POST':
        if(request.POST.get('update_member')):
            member_form=ExemplaryMembersForm(request.POST,request.FILES,instance=member_to_update)
            if(member_form.is_valid()):
                member_form.save()
                messages.info(request,f"Information for {member_to_update.member_name} was updated!")
                return redirect('central_branch:manage_exemplary_members')
    else:
        member_form=ExemplaryMembersForm(instance=member_to_update)
    context={
        'exemplary_member':member_to_update,
        'member_form':member_form
    }
    return render(request,"Manage Website/Exemplary Members/update_exemplary_member.html",context=context)

@login_required
def manage_view_access(request):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get access of the page first
    all_insb_members=port_render.get_all_registered_members(request)
    branch_data_access=Branch.get_branch_data_access(request)

    if request.method=="POST":
        if(request.POST.get('update_access')):
            ieee_id=request.POST['remove_member_data_access']
            
            # Setting Data Access Fields to false initially
            create_event_access=False
            event_details_page_access=False
            create_panels_access=False
            panel_memeber_add_remove_access=False
            team_details_page=False
            manage_web_access=False

            # Getting values from check box
            
            if(request.POST.get('create_event_access')):
                create_event_access=True
            if(request.POST.get('event_details_page_access')):
                event_details_page_access=True
            if(request.POST.get('create_panels_access')):
                create_panels_access=True
            if(request.POST.get('panel_memeber_add_remove_access')):
                panel_memeber_add_remove_access=True
            if(request.POST.get('team_details_page')):
                team_details_page=True
            if(request.POST.get('manage_web_access')):
                manage_web_access=True
            
            # ****The passed keys must match the field name in the models. otherwise it wont update access
            if(Branch.update_member_to_branch_view_access(request=request,ieee_id=ieee_id,kwargs={'create_event_access':create_event_access,
                                                       'event_details_page_access':event_details_page_access,
                                                       'create_panels_access':create_panels_access,'panel_memeber_add_remove_access':panel_memeber_add_remove_access,
                                                       'team_details_page':team_details_page,'manage_web_access':manage_web_access})):
                return redirect('central_branch:manage_access')
            
        if(request.POST.get('add_member_to_access')):
            selected_members=request.POST.getlist('member_select')
            if(Branch.add_member_to_branch_view_access(request=request,selected_members=selected_members)):
                return redirect('central_branch:manage_access')
        
        if(request.POST.get('remove_member')):
            ieee_id=request.POST['remove_member_data_access']
            if(Branch.remover_member_from_branch_access(request=request,ieee_id=ieee_id)):
                return redirect('central_branch:manage_access')

        

    context={
        'all_sc_ag':sc_ag,
        'insb_members':all_insb_members,
        'branch_data_access':branch_data_access,
    }

    return render(request,'Manage Access/manage_access.html',context)




# Create your views here.

@login_required
def event_control_homepage(request):
    # This function loads all events and super events in the event homepage table
    
        has_access_to_create_event=Branch_View_Access.get_create_event_access(request=request)

    # try:
        is_branch = True
        sc_ag=PortData.get_all_sc_ag(request=request)
        all_insb_events_with_interbranch_collaborations = Branch.load_all_inter_branch_collaborations_with_events(1)
        context={
            'all_sc_ag':sc_ag,
            'events':all_insb_events_with_interbranch_collaborations,
            # 'sc_ag_info':get_sc_ag_info,
            'has_access_to_create_event':has_access_to_create_event,
            'is_branch':is_branch,
            
        }

        if(request.method=="POST"):
            if request.POST.get('create_new_event'):
                print("Create")
            
            #Creating new event type for Group 1 
            elif request.POST.get('add_event_type'):
                event_type = request.POST.get('event_type')
                created_event_type = Branch.add_event_type_for_group(event_type,1)
                if created_event_type:
                    print("Event type did not exists, so new event was created")
                    messages.success(request,"New Event Type Added Successfully")
                else:
                    print("Event type already existed")
                    messages.info(request,"Event Type Already Exists")
                return redirect('central_branch:event_control')
            
        return render(request,'Events/event_homepage.html',context)
    # except Exception as e:
    #     logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
    #     ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
    #     # TODO: Make a good error code showing page and show it upon errror
    #     return HttpResponseBadRequest("Bad Request")
    

@login_required
def super_event_creation(request):

    '''function for creating super event'''

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        #calling it regardless to run the page
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,5)
        is_branch = True

        if request.method == "POST":

            '''Checking to see if either of the submit or cancelled button has been clicked'''

            if (request.POST.get('Submit')):

                '''Getting data from page and saving them in database'''

                super_event_name = request.POST.get('super_event_name')
                super_event_description = request.POST.get('super_event_description')
                start_date = request.POST.get('probable_date')
                end_date = request.POST.get('final_date')
                Branch.register_super_events(super_event_name,super_event_description,start_date,end_date)
                messages.success(request,"New Super Event Added Successfully")
                return redirect('central_branch:event_control')
            
        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'is_branch' : is_branch
        }
                        
        return render(request,"Events/Super Event/super_event_creation_form.html", context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def event_creation_form_page(request):
    
    #######load data to show in the form boxes#########
    try:
        form = EventForm()
        sc_ag=PortData.get_all_sc_ag(request=request)
        is_branch = True

        #loading super/mother event at first and event categories for Group 1 only (IEEE NSU Student Branch)
        super_events=Branch.load_all_mother_events()
        event_types=Branch.load_all_event_type_for_groups(1)
        
        '''function for creating event'''

        if(request.method=="POST"):

            ''' Checking to see if the next button is clicked '''

            if(request.POST.get('next')):



                '''Getting data from page and calling the register_event_page1 function to save the event page 1 to database'''

                event_name=request.POST['event_name']
                event_description=request.POST['event_description']
                super_event_id=request.POST.get('super_event')
                event_type_list = request.POST.getlist('event_type')
                event_date=request.POST['event_date']

                #It will return True if register event page 1 is success
                get_event=Branch.register_event_page1(
                    super_event_id=super_event_id,
                    event_name=event_name,
                    event_type_list=event_type_list,
                    event_description=event_description,
                    event_date=event_date
                )
                
                if(get_event)==False:
                    messages.error(request,"Database Error Occured! Please try again later.")
                else:
                    #if the method returns true, it will redirect to the new page
                    return redirect('central_branch:event_creation_form2',get_event)
            elif(request.POST.get('add_event_type')):
                ''' Adding a new event type '''
                event_type = request.POST.get('event_type')
                created_event_type = Branch.add_event_type_for_group(event_type,1)
                if created_event_type:
                    print("Event type did not exists, so new event was created")
                    messages.success(request,"New Event Type Added Successfully")
                else:
                    print("Event type already existed")
                    messages.info(request,"Event Type Already Exists")
                return redirect('central_branch:event_creation_form1')
        
        context={
            'super_events':super_events,
            'event_types':event_types,
            'is_branch' : is_branch,
            'all_sc_ag':sc_ag,
            'form':form,
            'is_branch':is_branch,
        }
                
        return render(request,'Events/event_creation_form.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")
        

@login_required
def event_creation_form_page2(request,event_id):
    #loading all inter branch collaboration Options

    try:
        is_branch=True
        sc_ag=PortData.get_all_sc_ag(request=request)
        inter_branch_collaboration_options=Branch.load_all_inter_branch_collaboration_options()
        is_branch = True
        
        if request.method=="POST":
            if(request.POST.get('next')):
                inter_branch_collaboration_list=request.POST.getlist('inter_branch_collaboration')
                intra_branch_collaboration=request.POST['intra_branch_collaboration']
                
                if(Branch.register_event_page2(
                    inter_branch_collaboration_list=inter_branch_collaboration_list,
                    intra_branch_collaboration=intra_branch_collaboration,
                    event_id=event_id)):
                    return redirect('central_branch:event_creation_form3',event_id)
                else:
                    messages.error(request,"Database Error Occured! Please try again later.")

            elif(request.POST.get('cancel')):
                return redirect('central_branch:event_control')
        
        context={
            'inter_branch_collaboration_options':inter_branch_collaboration_options,
            'all_sc_ag':sc_ag,
            'is_branch' : is_branch,
        }

        return render(request,'Events/event_creation_form2.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def event_creation_form_page3(request,event_id):
    try:
        is_branch=True
        sc_ag=PortData.get_all_sc_ag(request=request)
        #loading all venues from the venue list from event management team database
        venues=Events_And_Management_Team.getVenues()
        #loading all the permission criterias from event management team database
        permission_criterias=Events_And_Management_Team.getPermissionCriterias()

        is_branch = True

        if request.method=="POST":
            if request.POST.get('create_event'):
                #getting the venues for the event
                venue_list_for_event=request.POST.getlist('event_venues')
                #getting the permission criterias for the event
                permission_criterias_list_for_event=request.POST.getlist('permission_criteria')
                
                #updating data collected from part3 for the event
                update_event_details=Branch.register_event_page3(venue_list=venue_list_for_event,permission_criteria_list=permission_criterias_list_for_event,event_id=event_id)
                #if return value is false show an error message
                if(update_event_details==False):
                    messages.error(request, "An error Occured! Please Try again!")
                else:
                    messages.success(request, "New Event Added Succesfully")
                    return redirect('central_branch:event_control')
                
        context={
            'venues':venues,
            'permission_criterias':permission_criterias,
            'all_sc_ag':sc_ag,
            'is_branch' : is_branch,
        }

        return render(request,'Events/event_creation_form3.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")
    
@login_required
def get_updated_options_for_event_dashboard(request):
    #this function updates the select box upon the selection of the team in task assignation. takes event id as parameter. from html file, a script hits the api and fetches the returned dictionary
    
    if request.method == 'GET':
        # Retrieve the selected value from the query parameters
        selected_team = request.GET.get('team_id')

        # fetching the team member
        members=Branch.load_team_members(selected_team)
        updated_options = [
            # Add more options as needed
        ]
        for member in members:
            updated_options.append({'value': member.ieee_id, 'member_name': member.name,'position':member.position.role})

        #returning the dictionary
        return JsonResponse(updated_options, safe=False)
    
@login_required
def event_edit_form(request, event_id):

    ''' This function loads the edit page of events '''
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        # has_access = Branch.event_page_access(request)
        if True:
            is_branch = True
            is_event_published = Branch.load_event_published(event_id)
            is_flagship_event = Branch.is_flagship_event(event_id)
            is_registraion_fee_true = Branch.is_registration_fee_required(event_id)
            is_featured_event = Branch.is_featured_event(event_id)
            #Get event details from databse
            event_details = Events.objects.get(pk=event_id)

            if(request.method == "POST"):

                if('add_venues' in request.POST):
                    venue = request.POST.get('venue')
                    if(renderData.Branch.add_event_venue(venue)):
                        messages.success(request, "Venue created successfully")
                    else:
                        messages.error(request, "Something went wrong while creating the venue")
                    return redirect('central_branch:event_edit_form', event_id)
                
                
                if('update_event' in request.POST):
                    ''' Get data from form and call update function to update event '''

                    form_link = request.POST.get('drive_link_of_event')
                    publish_event_status = request.POST.get('publish_event')
                    flagship_event_status = request.POST.get('flagship_event')
                    registration_event_status = request.POST.get('registration_fee')
                    event_name=request.POST['event_name']
                    event_description=request.POST['event_description']
                    super_event_id=request.POST.get('super_event')
                    event_type_list = request.POST.getlist('event_type')
                    event_date=request.POST['event_date']
                    inter_branch_collaboration_list=request.POST.getlist('inter_branch_collaboration')
                    intra_branch_collaboration=request.POST['intra_branch_collaboration']
                    venue_list_for_event=request.POST.getlist('event_venues')
                    is_featured = request.POST.get('is_featured_event')
                    
                    #Checking to see of toggle button is on/True or off/False
                    publish_event = Branch.button_status(publish_event_status)
                    flagship_event = Branch.button_status(flagship_event_status)
                    registration_fee = Branch.button_status(registration_event_status)
                    is_featured = Branch.button_status(is_featured)

                    #if there is registration fee then taking the amount from field
                    if registration_fee:
                        registration_fee_amount = int(request.POST.get('registration_fee_amount'))
                    else:
                        registration_fee_amount=0
                    #Check if the update request is successful
                    if(renderData.Branch.update_event_details(event_id=event_id, event_name=event_name, event_description=event_description, super_event_id=super_event_id, event_type_list=event_type_list,publish_event = publish_event, event_date=event_date, inter_branch_collaboration_list=inter_branch_collaboration_list, intra_branch_collaboration=intra_branch_collaboration, venue_list_for_event=venue_list_for_event,
                                                            flagship_event = flagship_event,registration_fee = registration_fee,registration_fee_amount=registration_fee_amount,form_link = form_link,is_featured_event= is_featured)):
                        messages.success(request,f"EVENT: {event_name} was Updated successfully")
                        return redirect('central_branch:event_edit_form', event_id) 
                    else:
                        messages.error(request,"Something went wrong while updating the event!")
                        return redirect('central_branch:event_edit_form', event_id)
                    
                if request.POST.get('delete_event'):
                    ''' To delete event from databse '''
                    if(Branch.delete_event(event_id=event_id)):
                        messages.success(request,f"Event with EVENT ID {event_id} was Removed successfully")
                        return redirect('central_branch:event_control')
                    else:
                        messages.error(request,"Something went wrong while removing the event!")
                        return redirect('central_branch:event_control')

            form = EventForm({'event_description' : event_details.event_description})

            #loading super/mother event at first and event categories for depending on which group organised the event
            super_events=Branch.load_all_mother_events()
            event_types=Branch.load_all_event_type_for_groups(event_details.event_organiser.primary)

            inter_branch_collaboration_options=Branch.load_all_inter_branch_collaboration_options()

            # Get collaboration details
            interBranchCollaborations=Branch.event_interBranch_Collaborations(event_id=event_id)
            intraBranchCollaborations=Branch.event_IntraBranch_Collaborations(event_id=event_id)
            selected_venues = Branch.get_selected_venues(event_id=event_id)
            # Checking if event has collaborations
            hasCollaboration=False
            if(len(interBranchCollaborations)>0):
                hasCollaboration=True

            interBranchCollaborationsArray = []
            for i in interBranchCollaborations.all():
                interBranchCollaborationsArray.append(i.collaboration_with)

            #loading all venues from the venue list from event management team database
            venues=Events_And_Management_Team.getVenues()

            context={
                'all_sc_ag' : sc_ag,
                'is_branch' : is_branch,
                'event_details' : event_details,
                'event_id' : event_id,
                'form' : form,
                'super_events' : super_events,
                'event_types' : event_types,
                'inter_branch_collaboration_options' : inter_branch_collaboration_options,
                'interBranchCollaborations':interBranchCollaborationsArray,
                'intraBranchCollaborations':intraBranchCollaborations,
                'hasCollaboration' : hasCollaboration,
                'venues' : venues,
                'is_event_published':is_event_published,
                'is_flagship_event':is_flagship_event,
                'is_registration_fee_required':is_registraion_fee_true,
                'selected_venues':selected_venues,
                'is_featured_event':is_featured_event
            }

            return render(request, 'Events/event_edit_form.html', context)
        else:
            return redirect('main_website:event_details', event_id)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return HttpResponseBadRequest("Bad Request")



@login_required
def event_edit_media_form_tab(request, event_id):

    ''' This function loads the media tab page of events '''

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        # has_access = Branch.event_page_access(request)
        if(True):
            #Getting media links and images from database. If does not exist then they are set to none

            event_details = Events.objects.get(pk=event_id)
            try:
                media_links = Media_Link.objects.get(event_id = event_details)
            except:
                media_links = None
            media_images = Media_Images.objects.filter(event_id = event_details)
            number_of_uploaded_images = len(media_images)
            

            if request.method == "POST":

                if request.POST.get('save'):

                    #getting all data from page

                    folder_drive_link_for_event_pictures = request.POST.get('drive_link_of_event')
                    folder_drive_link_for_pictures_with_logos = request.POST.get('logo_drive_link_of_event')
                    selected_images = request.FILES.getlist('image')

                    if(MediaTeam.add_links_and_images(folder_drive_link_for_event_pictures,folder_drive_link_for_pictures_with_logos,
                                                selected_images,event_id)):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Please Fill All Fields Properly!')
                    return redirect("central_branch:event_edit_media_form_tab",event_id)
                
                if request.POST.get('remove_image'):

                    #When a particular picture is deleted, it gets the image url from the modal

                    image_url = request.POST.get('remove_image')
                    if(MediaTeam.remove_image(image_url,event_id)):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_media_form_tab",event_id)
        
            context={
                'is_branch' : True,
                'event_id' : event_id,
                'media_links' : media_links,
                'media_images':media_images,
                'media_url':settings.MEDIA_URL,
                'allowed_image_upload':6-number_of_uploaded_images,
                'all_sc_ag':sc_ag,
            }
            return render(request,"Events/event_edit_media_form_tab.html",context)
        else:
            return render(request, 'access_denied2.html')
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def event_edit_graphics_form_tab(request, event_id):

    ''' This function loads the graphics tab page of events '''

     #Initially loading the events whose  links and images were previously uploaded
    #and can be editible

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        #Get event details from databse
        # has_access = Branch.event_page_access(request)
        if(True):
            #Getting media links and images from database. If does not exist then they are set to none
            event_details = Events.objects.get(pk=event_id)
            try:
                graphics_link = Graphics_Link.objects.get(event_id = event_details)
            except:
                graphics_link = None
            try:
                graphic_banner_image = Graphics_Banner_Image.objects.get(event_id = event_details)
                image_number = 1
            except:
                graphic_banner_image = None
                image_number = 0

            
            if request.method == "POST":

                if request.POST.get('save'):

                    #getting all data from page
                    drive_link_folder = request.POST.get('drive_link_of_graphics')
                    selected_images = request.FILES.get('image')
                    if(GraphicsTeam.add_links_and_images(drive_link_folder,selected_images,event_id)):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Please Fill All Fields Properly!')
                    return redirect("central_branch:event_edit_graphics_form_tab",event_id)
                
                if request.POST.get('remove_image'):

                    #When a particular picture is deleted, it gets the image url from the modal

                    image_url = request.POST.get('remove_image')
                    if(GraphicsTeam.remove_image(image_url,event_id)):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_graphics_form_tab",event_id)

            context={
                'is_branch' : True,
                'event_id' : event_id,
                'all_sc_ag':sc_ag,
                'graphic_links' : graphics_link,
                'graphics_banner_image':graphic_banner_image,
                'media_url':settings.MEDIA_URL,
                'allowed_image_upload':1-image_number,

            }
            return render(request,"Events/event_edit_graphics_form_tab.html",context)
        else:
            return render(request, 'access_denied2.html')
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")
    
@login_required
def event_edit_graphics_form_links_sub_tab(request,event_id):
    ''' This function loads the graphics form link page of events '''

     #Initially loading the events whose  links and images were previously uploaded
    #and can be editible

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        all_graphics_link = GraphicsTeam.get_all_graphics_form_link(event_id)
        #Get event details from databse
        # event_details = Events.objects.get(pk=event_id)
        # has_access = Branch.event_page_access(request)
        if(True):

            if request.POST.get('add_link'):

                    form_link = request.POST.get('graphics_form_link')
                    title =request.POST.get('title')
                    if GraphicsTeam.add_graphics_form_link(event_id,form_link,title):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_graphics_form_links_sub_tab",event_id)
            
            if request.POST.get('update_link'):

                    form_link = request.POST.get('form_link')
                    title =request.POST.get('title')
                    pk = request.POST.get('link_pk')
                    if GraphicsTeam.update_graphics_form_link(form_link,title,pk):
                        messages.success(request,'Updated Successfully!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_graphics_form_links_sub_tab",event_id)

            if request.POST.get('remove_form_link'):

                    id = request.POST.get('remove_link')
                    if GraphicsTeam.remove_graphics_form_link(id):
                        messages.success(request,'Deleted Successfully!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_graphics_form_links_sub_tab",event_id)


            context={
                'is_branch' : True,
                'event_id' : event_id,
                'all_sc_ag':sc_ag,
                'all_graphics_link':all_graphics_link,

            }
            return render(request,"Events/event_edit_graphics_form_links_sub_tab.html",context)
        else:
            return render(request, 'access_denied2.html')
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")


@login_required
def event_edit_content_form_tab(request,event_id):
    ''' This function loads the content tab page of events '''

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        # has_access = Branch.event_page_access(request)
        if(True):
            all_notes_content = ContentWritingTeam.load_note_content(event_id)
            form = Content_Form()
            if(request.method == "POST"):               
                if 'add_note' in request.POST:
                    
                    #when the add button for submitting new note is clicked
                    title = request.POST['title']
                    note = request.POST['caption']

                    if ContentWritingTeam.creating_note(title,note,event_id):
                        messages.success(request,"Note created successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")

                    return redirect("central_branch:event_edit_content_form_tab",event_id)

                if 'remove' in request.POST:
                    id = request.POST.get('remove_note')
                    if ContentWritingTeam.remove_note(id):
                        messages.success(request,"Note deleted successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")
                    return redirect("central_branch:event_edit_content_form_tab",event_id)  

                if 'update_note' in request.POST:
                    print(request.POST)
                    id = request.POST['update_note']
                    title = request.POST['title']
                    note = request.POST['caption']
                    if(ContentWritingTeam.update_note(id, title, note)):
                        messages.success(request,"Note updated successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")
                    return redirect("central_branch:event_edit_content_form_tab",event_id)

            context={
                'is_branch' : True,
                'event_id' : event_id,
                'form_adding_note':form,
                'all_notes_content':all_notes_content,
                'all_sc_ag':sc_ag,

            }
            return render(request,"Events/event_edit_content_and_publications_form_tab.html",context)
        else:
            return render(request, 'access_denied2.html')
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
@xframe_options_exempt
def event_preview(request, event_id):
    ''' This function displays a preview of an event regardless of it's published status '''

    try:
        event = Events.objects.get(id=event_id)
        event_banner_image = HomepageItems.load_event_banner_image(event_id=event_id)
        event_gallery_images = HomepageItems.load_event_gallery_images(event_id=event_id)

        context = {
            'is_branch' : True,
            'event' : event,
            'media_url':settings.MEDIA_URL,
            'event_banner_image' : event_banner_image,
            'event_gallery_images' : event_gallery_images
        }

        return render(request, 'Events/event_description_main.html', context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def manage_toolkit(request):
    # get all toolkits
    all_toolkits=Toolkit.objects.all().order_by('-pk')
    if(request.method=="POST"):
        toolkit_form=ToolkitForm(request.POST,request.FILES)
        if(request.POST.get('add_item')):
            if(toolkit_form.is_valid()):
                toolkit_form.save()
                messages.success(request,"A new Toolkit Item was added!")
                return redirect('central_branch:manage_toolkit')
        if(request.POST.get('remove_toolkit')):
            item_to_delete=Toolkit.objects.get(pk=request.POST['toolkit_pk'])
            # first delete the picture from the filesystem
            if(os.path.isfile(item_to_delete.picture.path)):
                os.remove(item_to_delete.picture.path)
            item_to_delete.delete()
            messages.warning(request,"A Toolkit Item was deleted!")
            return redirect('central_branch:manage_toolkit')
    else:
        toolkit_form=ToolkitForm
    context={
        'all_toolkits':all_toolkits,
        'form':toolkit_form,
    }
    return render(request,"Manage Website/Publications/Toolkit/manage_toolkit.html",context=context)

@login_required
def update_toolkit(request,pk):
    # toolkit to update
    toolkit_to_update=get_object_or_404(Toolkit,pk=pk)
    if(request.method=="POST"):
        toolkit_form=ToolkitForm(request.POST,request.FILES,instance=toolkit_to_update)
        if(request.POST.get('update_toolkit_item')):
            if(toolkit_form.is_valid()):
                toolkit_form.save()
                messages.success(request,"Toolkit Item was updated!")
                return redirect('central_branch:manage_toolkit')
    else:
        toolkit_form=ToolkitForm(instance=toolkit_to_update)
    context={
        'toolkit':toolkit_to_update,
        'form':toolkit_form,
    }
    return render(request,"Manage Website/Publications/Toolkit/update_toolkit.html",context=context)
