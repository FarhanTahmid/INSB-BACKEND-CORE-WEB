from django.shortcuts import render,redirect
from django.http import HttpResponseBadRequest, JsonResponse

from django.contrib.auth.decorators import login_required
from users import renderData

@login_required
def getDashboardMiniChart1Stats(request):
    if request.method=="GET":
        #First get what the api is requesting form dashboard.init.js
        info_type=request.GET.get('event_stat')
        if(info_type == "event_number"):
            print("sakib")
            eventStat = renderData.getEventNumberStat()
            return JsonResponse(eventStat)
        else:
            return HttpResponseBadRequest()