from django.shortcuts import render
from port.renderData import PortData
from .get_sc_ag_info import SC_AG_Info

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
    
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info

    }
    return render(request,'Members/sc_ag_members.html',context=context)
