from django.shortcuts import render

# Create your views here.

def em_team_homepage(request):

    '''This function is responsible to load the main home page
    for the events and management team'''

    return render(request,"em_team_homepage.html")

def data_access(request):
    return render(request,"data_access_table.html")