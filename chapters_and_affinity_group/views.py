from django.shortcuts import render
from port.renderData import PortData
from users import renderData
from .get_sc_ag_info import SC_AG_Info
from port.renderData import PortData

# Create your views here.

def sc_ag_homepage(request,primary):
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
    
    
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info
    }
    return render(request,'Homepage/sc_ag_homepage.html',context)

def sc_ag_members(request,primary):
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
    # get all insb members
    all_insb_members=renderData.get_all_registered_members(request=request)
    # get sc_ag_positions
    sc_ag_positions=PortData.get_positions_with_sc_ag_id(request,sc_ag_primary=primary)
    # get sc_ag teams
    sc_ag_teams=PortData.get_teams_of_sc_ag_with_id(request,primary)
    
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info,
        'insb_members':all_insb_members,
        'positions':sc_ag_positions,
        'teams':sc_ag_teams
        
    }
    return render(request,'Members/sc_ag_members.html',context=context)
