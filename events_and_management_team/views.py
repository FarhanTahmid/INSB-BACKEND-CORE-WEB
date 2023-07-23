from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from system_administration.render_access import Access_Render
from events_and_management_team import renderData
from central_branch.renderData import Branch
from users.models import Members
from django.contrib import messages
from port.models import Roles_and_Position
from system_administration.models import EMT_Data_Access

# Create your views here.
@login_required
def em_team_homepage(request):

    '''This function is responsible to load the main home page
    for the events and management team'''

    return render(request,"em_team_homepage.html")

@login_required
def emt_data_access(request):

    # '''This function mantains all the data access works'''
    #Only sub eb of that team can access the page
    user = request.user
    has_access=(Access_Render.team_co_ordinator_access(team_id=renderData.Events_And_Management_Team.get_team_id(),username=user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username))
    
    data_access = renderData.Events_And_Management_Team.load_emt_data_access()
    team_members=renderData.Events_And_Management_Team.load_team_members()
    #load all position for insb members
    position=Branch.load_roles_and_positions()
    #load all insb members
    all_insb_members=Members.objects.all()

    if request.method=="POST":
        if request.POST.get('access_update'):
            
            task_assign_permission=False
            manage_team_permission=False

            #getting values from checkbox
            if(request.POST.get('task_assign')):
                task_assign_permission=True
            if(request.POST.get('manage_team')):
                manage_team_permission=True
            ieee_id=request.POST['access_ieee_id']

            if(renderData.Events_And_Management_Team.emt_access_modifications(
                ieee_id=ieee_id,assign_task_data_access_permission=task_assign_permission,manage_team_data_access_permission=manage_team_permission
            )):
                permission_updated_for=Members.objects.get(ieee_id=ieee_id)
                messages.info(request,f"Permission Details Was Updated for {permission_updated_for.name}")
            else:
                messages.info(request,f"Something Went Wrong! Please Contact System Administrator about this issue")
            

        if request.POST.get('access_remove'):
                
            '''To remove record from data access table'''
            
            ieeeId=request.POST['access_ieee_id']
            if(renderData.Events_And_Management_Team.remove_member_from_data_access(ieee_id=ieeeId)):
                messages.info(request,"Removed member from Data Access Table")
                return redirect('events_and_management_team:emt_data_access')
            else:
                messages.info(request,"Something went wrong!")
            
        if request.POST.get('remove_member'):
            '''To remove member from team table'''
            try:
                Members.objects.filter(ieee_id=request.POST['remove_ieee_id']).update(team=None,position=Roles_and_Position.objects.get(id=13))
                try:
                    EMT_Data_Access.objects.filter(ieee_id=request.POST['remove_ieee_id']).delete()
                except EMT_Data_Access.DoesNotExist:
                    return redirect('events_and_management_team:emt_data_access')
                return redirect('events_and_management_team:emt_data_access')
            except:
                pass

        if request.POST.get('update_data_access_member'):
            
            new_data_access_member_list=request.POST.getlist('member_select')
            
            if(len(new_data_access_member_list)>0):
                for ieeeID in new_data_access_member_list:
                    if(renderData.Events_And_Management_Team.add_member_to_data_access(ieeeID)=="exists"):
                        messages.info(request,f"The member with IEEE Id: {ieeeID} already exists in the Data Access Table")
                    elif(renderData.Events_And_Management_Team.add_member_to_data_access(ieeeID)==False):
                        messages.info(request,"Something Went wrong! Please try again")
                    elif(renderData.Events_And_Management_Team.add_member_to_data_access(ieeeID)==True):
                        messages.info(request,f"Member with {ieeeID} was added to the Data Access table!")
                        return redirect('events_and_management_team:emt_data_access')
            
        if request.POST.get('add_member_to_team'):
            #get selected members
            members_to_add=request.POST.getlist('member_select1')
            #get position
            position=request.POST.get('position')
            for member in members_to_add:
                renderData.Events_And_Management_Team.add_member_to_team(member,position)
            return redirect('events_and_management_team:emt_data_access')
            
    context={
        'data_access':data_access,
        'members':team_members,
        'insb_members':all_insb_members,
        'positions':position
        
    }

    if(has_access):
        return render(request,'emt_data_access_table.html',context=context)
    else:
        return render(request,"emt_access_denied.html")
    
@login_required
def emt_task_assign(request):

    user = request.user
    has_access = renderData.Events_And_Management_Team.task_assign_view_control(user.username)
    
    if has_access:
        return render(request,"emt_task_assign.html")
    else:
        return render(request,"emt_access_denied.html")
