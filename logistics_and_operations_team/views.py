from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from system_administration.render_access import Access_Render
from .renderData import LogisticsTeam
from users.models import Members
from central_branch.renderData import Branch
from system_administration.models import LAO_Data_Access
from port.models import Roles_and_Position
from django.contrib import messages
from port.renderData import PortData
from users.renderData import PanelMembersData
# Create your views here.
@login_required
def team_homepage(request):
    sc_ag=PortData.get_all_sc_ag(request=request)

    # get all members of the team
    
    get_officers=LogisticsTeam.load_officers()
    get_volunteers=LogisticsTeam.load_volunteers()
    
    context={
        'all_sc_ag':sc_ag,
        'co_ordinators':get_officers[0],
        'incharges':get_officers[1],
        'core_volunteers':get_volunteers[0],
        'team_volunteers':get_volunteers[1],
    }
    return render(request,"Homepage/team_homepage.html",context=context)
@login_required
def manage_team(request):
    '''This function loads the manage team page for logistics and operations team and is accessable
    by the co-ordinatior only, unless the co-ordinators gives access to others as well'''
    sc_ag=PortData.get_all_sc_ag(request=request)
    
    user = request.user
    has_access=(Access_Render.team_co_ordinator_access(team_id=LogisticsTeam.get_team_id(),username=user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username)
    or LogisticsTeam.lao_manage_team_access(user.username))

    if(has_access):
        data_access = LogisticsTeam.load_manage_team_access()
        team_members = LogisticsTeam.load_team_members()
        #load all position for insb members
        position=PortData.get_all_volunteer_position_with_sc_ag_id(request=request,sc_ag_primary=1)
        #load all insb members
        all_insb_members=Members.objects.all()

        if request.method == "POST":
            if (request.POST.get('add_member_to_team')):
                #get selected members
                members_to_add=request.POST.getlist('member_select1')
                #get position
                position=request.POST.get('position')
                for member in members_to_add:
                    LogisticsTeam.add_member_to_team(member,position)
                return redirect('logistics_and_operations_team:manage_team')

            if (request.POST.get('remove_member')):
                '''To remove member from team table'''
                try:
                    current_panel=Branch.load_current_panel()
                    PanelMembersData.remove_member_from_panel(request=request,panel_id=current_panel.pk,ieee_id=request.POST['remove_ieee_id'])
                    try:
                        LAO_Data_Access.objects.filter(ieee_id=request.POST['remove_ieee_id']).delete()
                    except LAO_Data_Access.DoesNotExist:
                        return redirect('logistics_and_operations_team:manage_team')
                    return redirect('logistics_and_operations_team:manage_team')
                except:
                    pass

            if request.POST.get('access_update'):
                manage_team_access = False
                if(request.POST.get('manage_team_access')):
                    manage_team_access=True
                ieee_id=request.POST['access_ieee_id']

                if (LogisticsTeam.lao_manage_team_access_modifications(manage_team_access,ieee_id)):
                    permission_updated_for=Members.objects.get(ieee_id=ieee_id)
                    messages.info(request,f"Permission Details Was Updated for {permission_updated_for.name}")
                else:
                    messages.info(request,f"Something Went Wrong! Please Contact System Administrator about this issue")

            if request.POST.get('access_remove'):
                '''To remove record from data access table'''
                
                ieeeId=request.POST['access_ieee_id']
                if(LogisticsTeam.remove_member_from_manage_team_access(ieee_id=ieeeId)):
                    messages.info(request,"Removed member from Managing Team")
                    return redirect('logistics_and_operations_team:manage_team')
                else:
                    messages.info(request,"Something went wrong!")
            if request.POST.get('update_data_access_member'):
                
                new_data_access_member_list=request.POST.getlist('member_select')
                
                if(len(new_data_access_member_list)>0):
                    for ieeeID in new_data_access_member_list:
                        if(LogisticsTeam.add_member_to_manage_team_access(ieeeID)=="exists"):
                            messages.info(request,f"The member with IEEE Id: {ieeeID} already exists in the Data Access Table")
                        elif(LogisticsTeam.add_member_to_manage_team_access(ieeeID)==False):
                            messages.info(request,"Something Went wrong! Please try again")
                        elif(LogisticsTeam.add_member_to_manage_team_access(ieeeID)==True):
                            messages.info(request,f"Member with {ieeeID} was added to the team table!")
                            return redirect('logistics_and_operations_team:manage_team')

            
        context={
            'all_sc_ag':sc_ag,
            'data_access':data_access,
            'members':team_members,
            'insb_members':all_insb_members,
            'positions':position,
            
        }
        return render(request,"logistics_and_operations_team\Manage Team\manage_team.html",context=context)
    else:
        return render(request,"logistics_and_operations_team/access_denied.html", {'all_sc_ag':sc_ag,})