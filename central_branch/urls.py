import imp
from django.urls import path,include
from . import views

app_name='central_branch'

##defining the urls to work with

urlpatterns = [
    
    #central_homeage
    path('',views.central_home, name='central_home'),
    #Event control page 
    path('event_control',views.event_control_homepage, name='event_control'),
    #Event Creation Form page 1
    path('create_event/',views.event_creation_form_page,name='event_creation_form1'),
    #Event Creation Form Page 2
    path("create_event/<int:event_id>/page-2", views.event_creation_form_page2, name="event_creation_form2"),
    #Event creation page 3
    path("create_event/<int:event_id>/page-3", views.event_creation_form_page3, name="event_creation_form3"),
    #event dashboard team
    path('event_details/<int:event_id>',views.event_description,name='event_dashboard'),
    #teams page
    path('teams_and_panels',views.teams,name='teams'),
    #team details page
    path('team_details/<int:primary>/<str:name>',views.team_details,name='team_details'),
    #manage team Page
    path('manage_team/<str:pk>/<str:team_name>',views.manage_team,name="manage_team"),
    
    #PANEL
    #panel details
    path('panel_details/<int:pk>',views.panel_details,name="panel_details"),
    
    
    #for updating value in team member select box in event assigning
    path('get_updated_options/', views.get_updated_options_for_event_dashboard, name='get_updated_options'),
    #others page
    path('others/',views.others,name="others"),
    #addresearch page
    path('add_research/',views.add_research,name="add_research"),
    #addblogs page
    path('add_blogs/',views.add_blogs,name="add_blogs"),
    #Super Event Creation Form
    path('create_super_event/',views.super_event_creation,name="super_event_creation")
    
]