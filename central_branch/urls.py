import imp
from django.urls import path,include
from . import views

app_name='central_branch'

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
    #Event creation page 3
    path("create_event/<int:event_id>/page-3", views.event_creation_form_page3, name="event_creation_form3"),
    #Event control homepage
    path("event_control/event_home/<int:event_id>", views.event_control_homepage,name="event_homepage"),
    #teams page
    path('teams',views.teams,name='teams'),
    #team details page
    path('team_details/<str:pk>/<str:name>',views.team_details,name='team_details'),
    #event dashboard team
    path('event_dashboard/<int:event_id>',views.event_dashboard,name='event_dashboard'),
    #others page
    path('others/',views.others,name="others"),
    #addresearch page
    path('add_research/',views.add_research,name="add_research"),
    #addblogs page
    path('add_blogs/',views.add_blogs,name="add_blogs")
    
]