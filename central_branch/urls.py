import imp
from django.urls import path,include
from . import views

app_name='central_branch'

##defining the urls to work with

urlpatterns = [
    
    #central_homeage
    path('',views.central_home, name='central_home'),
    #teams page
    path('teams/',views.teams,name='teams'),
    #team details page
    path('team_details/<int:primary>/<str:name>',views.team_details,name='team_details'),
    #manage team Page
    path('manage_team/<str:pk>/<str:team_name>',views.manage_team,name="manage_team"),

    #PANEL
    path('panels',views.panel_home,name="panels"),
    #panel details
    path('panels/<int:panel_id>',views.panel_details,name="panel_details"),
    
    
    #for updating value in team member select box in event assigning
    # path('get_updated_options/', views.get_updated_options_for_event_dashboard, name='get_updated_options'),
    #others page
    path('others/',views.others,name="others"),
    #addresearch page
    path('add_research/',views.add_research,name="add_research"),
    #addblogs page
    path('add_blogs/',views.add_blogs,name="add_blogs"),
    
    #WEBSITE Management URL Path
    path('manage_website/homepage',views.manage_website_homepage,name="manage_website_home"),

    path('manage_access',views.manage_view_access,name="manage_access"),

]