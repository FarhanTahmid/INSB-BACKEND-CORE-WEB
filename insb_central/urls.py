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
    #Event Creation Form page 1
    path('create_event/page-1',views.event_creation_form_page1,name='event_creation_form1'),
    #Event Creation Form Page 2
    path("create_event/<int:event_id>/page-2", views.event_creation_form_page2, name="event_creation_form2"),
    #teams page
    path('teams',views.teams,name='teams'),
    #team details page
    path('team_details/<str:pk>/<str:name>',views.team_details,name='team_details'),
    
]
