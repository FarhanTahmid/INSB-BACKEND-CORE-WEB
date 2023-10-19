from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
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
from central_branch.models import Events

# Create your views here.
@login_required
def team_homepage(request):

    #Loading data of the co-ordinators, co ordinator id is 9,
    co_ordinators=renderData.GraphicsTeam.get_member_with_postion(9)
    #Loading data of the incharges, incharge id is 10
    in_charges=renderData.GraphicsTeam.get_member_with_postion(10)
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
    by the co-ordinatior only, unless the co-ordinators gives access to others as well'''
    user = request.user
    has_access=(Access_Render.team_co_ordinator_access(team_id=GraphicsTeam.get_team_id(),username=user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username)
    or GraphicsTeam.graphics_manage_team_access(user.username))

    data_access = GraphicsTeam.load_manage_team_access()
    team_members = GraphicsTeam.load_team_members()
    #load all position for insb members
    position=Branch.load_roles_and_positions()
    #load all insb members
    all_insb_members=Members.objects.all()

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
            ieee_id=request.POST['access_ieee_id']
            if (GraphicsTeam.graphics_manage_team_access_modifications(manage_team_access,ieee_id)):
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
        'positions':position,
        
    }

    if has_access:
        return render(request,"graphics_team/manage_team.html",context=context)
    return render(request,"access_denied2.html")

@login_required
def event_page(request):

    '''Only events organised by INSB would be shown on the event page of Graphics Team
       So, only those events are being retrieved from database'''
    insb_organised_events = Events.objects.filter(event_organiser=5).order_by('-event_date')
   
   
    context = {'events_of_insb_only':insb_organised_events,
                }


    return render(request,"Events/graphics_team_events.html",context)

@login_required
def event_form(request,event_ID):

    #Initially loading the events whose  links and images were previously uploaded
    #and can be editible

    event_id = event_ID
    event = Events.objects.get(id = event_id)

    context={
        'event_name':event.event_name,
    }

    return render(request,"graphics_team/graphics_event_form.html",context)