import imp
from django.urls import path,include
from . import views

app_name='insb_central'

##defining the urls to work with

urlpatterns = [
    
    #central_homeage
    path('',views.central_home, name='central_home'),
    #Event control page 
    path('event_control',views.event_control, name='event_control'),
    #Event Creation Form
    path('create_event',views.event_creation_form,name='event_creation_form'),
    #teams page
    path('teams',views.teams,name='teams'),
    #team details page
    path('team_details/<str:pk>/<str:name>',views.team_details,name='team_details'),
    
]
