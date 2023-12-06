from django.shortcuts import render,redirect
from port.renderData import PortData
from users import renderData
from .get_sc_ag_info import SC_AG_Info
from .renderData import Sc_Ag
from port.renderData import PortData
from system_administration.system_error_handling import ErrorHandling
from central_branch.renderData import Branch
from datetime import datetime
from django.http import Http404,HttpResponseBadRequest
import logging
import traceback


# Create your views here.
logger=logging.getLogger(__name__)

def sc_ag_homepage(request,primary):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        
        
        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info
        }
        return render(request,'Homepage/sc_ag_homepage.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

def sc_ag_members(request,primary):
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
    # get all insb members
    all_insb_members=renderData.get_all_registered_members(request=request)
    # get sc_ag_positions
    sc_ag_positions=PortData.get_positions_with_sc_ag_id(request,sc_ag_primary=primary)
    # get sc_ag teams
    sc_ag_teams=PortData.get_teams_of_sc_ag_with_id(request,primary)
    # get sc_ag members
    sc_ag_members=SC_AG_Info.get_sc_ag_members(request,primary)
    
    if request.method=="POST":
        if request.POST.get('add_sc_ag_member'):
            position = request.POST['position']
            if position=='0':
                position=None
            team=request.POST['team']
            if team=='0':
                team=None
            member_ieee_id_list=request.POST.getlist('member_select')
            
            # Create Member for SC AG
            Sc_Ag.add_insb_members_to_sc_ag(ieee_id_list=member_ieee_id_list,
                                            position_id=position,
                                            sc_ag_primary=primary,
                                            team_pk=team,
                                            request=request)
            return redirect('chapters_and_affinity_group:sc_ag_members',primary)
                
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info,
        'insb_members':all_insb_members,
        'positions':sc_ag_positions,
        'teams':sc_ag_teams,
        'sc_ag_members':sc_ag_members,
        'member_count':len(sc_ag_members)
        
    }
    return render(request,'Members/sc_ag_members.html',context=context)

def sc_ag_panels(request,primary):
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
    
    # get panels of SC-AG
    all_panels=SC_AG_Info.get_panels_of_sc_ag(request=request,sc_ag_primary=primary)
    
    if request.method=="POST":
        if request.POST.get('create_panel'):
            tenure_year=request.POST['tenure_year']
            panel_start_date=request.POST['panel_start_date']
            panel_end_date=request.POST['panel_end_date']
            current_check=request.POST.get('current_check')
            if current_check is None:
                current_check=False
            else:
                current_check=True
            
            if(Sc_Ag.create_new_panel_of_sc_ag(request=request,
                                            current_check=current_check,
                                            panel_end_time=panel_end_date,
                                            panel_start_time=panel_start_date,
                                            sc_ag_primary=primary,tenure_year=tenure_year)
              ):
                return redirect('chapters_and_affinity_group:sc_ag_panels',primary)  
    
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info,
        'panels':all_panels,
        
    }
    return render(request,'Panels/panel_homepage.html',context=context)

def sc_ag_panel_details(request,primary,panel_pk):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        
        # get sc_ag members
        sc_ag_members=SC_AG_Info.get_sc_ag_members(request,primary)
        
        # get panel information
        panel_info=Branch.load_panel_by_id(panel_pk)
        # getting tenure time
        if(panel_info.panel_end_time is None):
            present_date=datetime.now()
            tenure_time=present_date.date()-panel_info.creation_time.date()
        else:
            tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()

        # get sc_ag_executives
        sc_ag_eb_members=SC_AG_Info.get_sc_ag_executives_from_panels(request=request,panel_id=panel_pk)
        
        if request.method=="POST":
            # adding member to panel
            if request.POST.get('add_executive_to_sc_ag_panel'):
                member_select_list=request.POST.getlist('member_select')
                position=request.POST.get('sc_ag_eb_position')
                # Add Executive members to panel, keeping team=None
                if(Sc_Ag.add_sc_ag_members_to_panel(memberList=member_select_list,panel_id=panel_pk,position_id=position,request=request,team=None,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)
            # removing member from panel
            if request.POST.get('remove_member'):
                member_to_remove=request.POST['remove_panel_member']
                if(Sc_Ag.remove_sc_ag_member_from_panel(request=request,member_ieee_id=member_to_remove,panel_id=panel_pk,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)
            
            # Delete panel
            if(request.POST.get('delete_panel')):
                if(Sc_Ag.delete_sc_ag_panel(request=request,panel_pk=panel_pk,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panels',primary)
            
            # update panel settings
            if(request.POST.get('save_changes')):
                panel_tenure=request.POST['panel_tenure']
                current_panel_check=request.POST.get('current_panel_check')
                if current_panel_check is None:
                    current_panel_check=False
                else:
                    current_panel_check=True
                panel_start_date=request.POST['panel_start_date']
                panel_end_date=request.POST['panel_end_date']
                if(Sc_Ag.update_sc_ag_panel(is_current_check=current_panel_check,panel_end_date=panel_end_date,panel_pk=panel_pk,panel_start_date=panel_start_date,panel_tenure=panel_tenure,request=request,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)
                

        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'panel_info':panel_info,
            'tenure_time':tenure_time,
            'sc_ag_members':sc_ag_members,
            'sc_ag_eb_members':sc_ag_eb_members,
            'sc_ag_eb_positions':SC_AG_Info.get_sc_ag_executive_positions(request=request,sc_ag_primary=primary)
        }
        return render(request,'Panels/sc_ag_executive_members_tab.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request") 
                
def sc_ag_panel_details_officers_tab(request,primary,panel_pk):
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)

    # get panel information
    panel_info=Branch.load_panel_by_id(panel_pk)
    # getting tenure time
    if(panel_info.panel_end_time is None):
        present_date=datetime.now()
        tenure_time=present_date.date()-panel_info.creation_time.date()
    else:
        tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()

    # get sc_ag_officer members
    sc_ag_officer_members_in_panel=SC_AG_Info.get_sc_ag_officers_from_panels(panel_id=panel_pk,request=request)
    # get sc_ag members
    sc_ag_members=SC_AG_Info.get_sc_ag_members(request,primary)
    
    if(request.method=="POST"):
        # Add Member to officer panel
        if(request.POST.get('add_officer_to_sc_ag_panel')):
            member_select_list=request.POST.getlist('member_select')
            position=request.POST.get('sc_ag_officer_position')
            team=request.POST.get('sc_ag_team')
            if(Sc_Ag.add_sc_ag_members_to_panel(memberList=member_select_list,panel_id=panel_pk,position_id=position,team=team,sc_ag_primary=primary,request=request)):
                return redirect('chapters_and_affinity_group:sc_ag_panel_details_officers', primary,panel_pk)
        
        # Remove Member from Panel
        if request.POST.get('remove_member_officer'):
            member_to_remove=request.POST['remove_officer_member']
            if(Sc_Ag.remove_sc_ag_member_from_panel(request=request,member_ieee_id=member_to_remove,panel_id=panel_pk,sc_ag_primary=primary)):
                return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)
        
        
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info,
        'panel_info':panel_info,
        'tenure_time':tenure_time,
        'sc_ag_members':sc_ag_members,
        'sc_ag_officer_member':sc_ag_officer_members_in_panel,
        'sc_ag_officer_positions':SC_AG_Info.get_sc_ag_officer_positions(request=request,sc_ag_primary=primary),
        'sc_ag_teams':SC_AG_Info.get_teams_of_sc_ag(request=request,sc_ag_primary=primary),

    }
    return render(request,'Panels/sc_ag_officer_members_tab.html',context=context)

def sc_ag_panel_details_volunteers_tab(request,primary,panel_pk):
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)

    # get panel information
    panel_info=Branch.load_panel_by_id(panel_pk)
    # getting tenure time
    if(panel_info.panel_end_time is None):
        present_date=datetime.now()
        tenure_time=present_date.date()-panel_info.creation_time.date()
    else:
        tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()

    # get sc_ag members
    sc_ag_members=SC_AG_Info.get_sc_ag_members(request,primary)
    # get sc ag volunteer positions
    sc_ag_volunteer_positions=PortData.get_all_volunteer_position_with_sc_ag_id(request=request,sc_ag_primary=primary)
    
    # get_sc_ag_officer members from panels
    sc_ag_volunteer_members_in_panel=SC_AG_Info.get_sc_ag_volunteer_from_panels(request=request,panel_id=panel_pk)
    
    if(request.method=="POST"):
        # Add Member to officer panel
        if(request.POST.get('add_volunteer_to_sc_ag_panel')):
            member_select_list=request.POST.getlist('member_select')
            position=request.POST.get('sc_ag_volunteer_position')
            team=request.POST.get('sc_ag_team')
            if(Sc_Ag.add_sc_ag_members_to_panel(memberList=member_select_list,panel_id=panel_pk,position_id=position,team=team,sc_ag_primary=primary,request=request)):
                return redirect('chapters_and_affinity_group:sc_ag_panel_details_volunteers', primary,panel_pk)
        
        # Remove Member from Panel
        if request.POST.get('remove_member_volunteer'):
            member_to_remove=request.POST['remove_volunteer_member']
            if(Sc_Ag.remove_sc_ag_member_from_panel(request=request,member_ieee_id=member_to_remove,panel_id=panel_pk,sc_ag_primary=primary)):
                return redirect('chapters_and_affinity_group:sc_ag_panel_details_volunteers', primary,panel_pk)

    
    
    
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info,
        'panel_info':panel_info,
        'tenure_time':tenure_time,
        'sc_ag_members':sc_ag_members,
        'sc_ag_volunteer_positions':sc_ag_volunteer_positions,
        'sc_ag_teams':SC_AG_Info.get_teams_of_sc_ag(request=request,sc_ag_primary=primary),
        'sc_ag_volunteer_members':sc_ag_volunteer_members_in_panel,
    }
    return render(request,'Panels/sc_ag_volunteer_members_tab.html',context=context)

def sc_ag_panel_details_alumni_members_tab(request,primary,panel_pk):
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)

    # get panel information
    panel_info=Branch.load_panel_by_id(panel_pk)
    # getting tenure time
    if(panel_info.panel_end_time is None):
        present_date=datetime.now()
        tenure_time=present_date.date()-panel_info.creation_time.date()
    else:
        tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()

    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info,
        'panel_info':panel_info,
        'tenure_time':tenure_time,

    }
    return render(request,'Panels/sc_ag_alumni_members_tab.html',context=context)