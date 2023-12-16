from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from graphics_team.manage_access import GraphicsTeam_Render_Access
from system_administration.render_access import Access_Render
from users.models import Members
from central_branch.renderData import Branch
from port.models import Roles_and_Position
from django.contrib import messages
from system_administration.models import Graphics_Data_Access
from .renderData import GraphicsTeam
from users.renderData import LoggedinUser
from . import renderData
from django.conf import settings
from central_events.models import Events
from .models import Graphics_Banner_Image,Graphics_Link
import traceback
import logging
from system_administration.system_error_handling import ErrorHandling
from django.http import Http404,HttpResponseBadRequest
from datetime import datetime
from port.renderData import PortData


logger=logging.getLogger(__name__)
# Create your views here.
@login_required
def team_homepage(request):
    
    co_ordinators=renderData.GraphicsTeam.get_co_ordinator()
    in_charges=renderData.GraphicsTeam.get_officer()
    print(in_charges)
    current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file
    context={
        'co_ordinators':co_ordinators,
        'incharges':in_charges,
        'media_url':settings.MEDIA_URL,
        'user_data':user_data,
    }


    return render(request,"Homepage/graphics_homepage.html",context)

@login_required
def manage_team(request):
    '''This function loads the manage team page for graphics team and is accessable
    by the co-ordinatiors and other admin users only, unless the co-ordinators gives access to others as well'''

    has_access = GraphicsTeam_Render_Access.get_common_access(request)
    if has_access:
        data_access = GraphicsTeam.load_data_access()
        team_members = GraphicsTeam.load_team_members()
        #load all position for insb members
        position=Branch.load_roles_and_positions()

        # Excluding position of EB, Faculty and SC-AG members
        for i in position:
            if(i.is_eb_member or i.is_faculty or i.is_sc_ag_eb_member):
                position=position.exclude(pk=i.pk)
                
        #load all insb members
        all_insb_members=Members.objects.all()
        #load all current panel members
        current_panel_members = Branch.load_current_panel_members()

        if request.method == "POST":
            if (request.POST.get('add_member_to_team')):
                #get selected members
                members_to_add=request.POST.getlist('member_select1')
                #get position
                position=request.POST.get('position')
                for member in members_to_add:
                    GraphicsTeam.add_member_to_team(member,position)
                return redirect('graphics_team:manage_team')
            
            if (request.POST.get('remove_member')):
                '''To remove member from team table'''
                try:
                    Members.objects.filter(ieee_id=request.POST['remove_ieee_id']).update(team=None,position=Roles_and_Position.objects.get(id=13))
                    try:
                        Graphics_Data_Access.objects.filter(ieee_id=request.POST['remove_ieee_id']).delete()
                    except Graphics_Data_Access.DoesNotExist:
                        return redirect('graphics_team:manage_team')
                    return redirect('graphics_team:manage_team')
                except:
                    pass

            if request.POST.get('access_update'):
                manage_team_access = False
                if(request.POST.get('manage_team_access')):
                    manage_team_access=True
                event_access=False
                if(request.POST.get('event_access')):
                    event_access=True
                ieee_id=request.POST['access_ieee_id']
                if (GraphicsTeam.graphics_manage_team_access_modifications(manage_team_access, event_access, ieee_id)):
                    permission_updated_for=Members.objects.get(ieee_id=ieee_id)
                    messages.info(request,f"Permission Details Was Updated for {permission_updated_for.name}")
                else:
                    messages.info(request,f"Something Went Wrong! Please Contact System Administrator about this issue")

            if request.POST.get('access_remove'):
                '''To remove record from data access table'''
                
                ieeeId=request.POST['access_ieee_id']
                if(GraphicsTeam.remove_member_from_manage_team_access(ieee_id=ieeeId)):
                    messages.info(request,"Removed member from Managing Team")
                    return redirect('graphics_team:manage_team')
                else:
                    messages.info(request,"Something went wrong!")

            if request.POST.get('update_data_access_member'):
                
                new_data_access_member_list=request.POST.getlist('member_select')
                
                if(len(new_data_access_member_list)>0):
                    for ieeeID in new_data_access_member_list:
                        if(GraphicsTeam.add_member_to_manage_team_access(ieeeID)=="exists"):
                            messages.info(request,f"The member with IEEE Id: {ieeeID} already exists in the Data Access Table")
                        elif(GraphicsTeam.add_member_to_manage_team_access(ieeeID)==False):
                            messages.info(request,"Something Went wrong! Please try again")
                        elif(GraphicsTeam.add_member_to_manage_team_access(ieeeID)==True):
                            messages.info(request,f"Member with {ieeeID} was added to the team table!")
                            return redirect('graphics_team:manage_team')

        context={
            'data_access':data_access,
            'members':team_members,
            'insb_members':all_insb_members,
            'current_panel_members':current_panel_members,
            'positions':position,
            
        }  
        return render(request,"graphics_team/manage_team.html",context=context)
    else:
        return render(request,"access_denied2.html")

@login_required
def event_page(request):

    '''Only events organised by INSB would be shown on the event page of Graphics Team
       So, only those events are being retrieved from database'''
    insb_organised_events = Branch.load_insb_organised_events()
   
   
    context = {
        'events_of_insb_only':insb_organised_events,
    }


    return render(request,"Events/graphics_team_events.html",context)

@login_required
def event_form(request,event_id):

    #Initially loading the events whose  links and images were previously uploaded
    #and can be editible

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access = GraphicsTeam_Render_Access.access_for_events(request)
        if(has_access):
            #Getting media links and images from database. If does not exist then they are set to none
            try:
                graphics_link = Graphics_Link.objects.get(event_id = Events.objects.get(pk=event_id))
            except:
                graphics_link = None
            try:
                graphic_banner_image = Graphics_Banner_Image.objects.get(event_id = Events.objects.get(pk=event_id))
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
                    return redirect("graphics_team:event_form",event_id)
                
                if request.POST.get('remove_image'):

                    #When a particular picture is deleted, it gets the image url from the modal

                    image_url = request.POST.get('remove_image')
                    if(GraphicsTeam.remove_image(image_url,event_id)):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("graphics_team:event_form",event_id)

            context={
                'all_sc_ag':sc_ag,
                'graphic_links' : graphics_link,
                'graphics_banner_image':graphic_banner_image,
                'media_url':settings.MEDIA_URL,
                'allowed_image_upload':1-image_number,

            }
            return render(request,"Events/graphics_event_form.html",context)
        else:
            return redirect('main_website:event_details', event_id)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")