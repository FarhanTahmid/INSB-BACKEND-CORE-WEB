from django.shortcuts import render
from port.renderData import PortData
# Create your views here.

def sc_ag_homepage(request,primary):
    sc_ag=PortData.get_all_sc_ag(request=request)

    context={
        'all_sc_ag':sc_ag,
    }
    return render(request,'Homepage/homepage.html',context)