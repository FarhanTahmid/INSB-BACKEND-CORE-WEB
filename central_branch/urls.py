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
    path('panels/<int:panel_id>',views.branch_panel_details,name="panel_details"),
    path('panels/<int:panel_id>/officers',views.branch_panel_officers_tab,name="panel_details_officers"),
    path('panels/<int:panel_id>/volunteers',views.branch_panel_volunteers_tab,name="panel_details_volunteers"),
    path('panels/<int:panel_id>/alumni',views.branch_panel_alumni_tab,name="panel_details_alumni"),

    
    #for updating value in team member select box in event assigning
    # path('get_updated_options/', views.get_updated_options_for_event_dashboard, name='get_updated_options'),
    #others page
    path('others/',views.others,name="others"),
    
    
    #WEBSITE Management URL Path
    path('manage_website/homepage',views.manage_website_homepage,name="manage_website_home"),
    path('manage_website/achievements',views.manage_achievements,name="manage_achievements"),
    path('manage_website/achievements/update/<int:pk>',views.update_achievements,name="achievements_update"),
    path('manage_website/news',views.manage_news,name="manage_news"),
    path('manage_website/news/update/<int:pk>',views.update_news,name="update_news"),
    path('manage_website/blogs',views.manage_blogs,name="manage_blogs"),
    path('manage_website/blogs/update/<int:pk>',views.update_blogs,name="update_blogs"),
    path('manage_website/research',views.manage_research,name="manage_research"),
    path('manage_website/research/update/<int:pk>',views.update_researches,name="update_researches"),
    
    
    
    path('manage_access',views.manage_view_access,name="manage_access"),

    #Events urls
    #Event control page 
    path('events',views.event_control_homepage, name='event_control'),
    #Event Creation Form page 1
    path('events/create_event/',views.event_creation_form_page,name='event_creation_form1'),
    #Event Creation Form Page 2
    path("events/create_event/<int:event_id>/page-2", views.event_creation_form_page2, name="event_creation_form2"),
    #Event creation page 3
    path("events/create_event/<int:event_id>/page-3", views.event_creation_form_page3, name="event_creation_form3"),
    #Event edit page
    path('event_details/<int:event_id>/edit/',views.event_edit_form,name='event_edit_form'),
    #Event media tab page
    path('event_details/<int:event_id>/edit/media',views.event_edit_media_form_tab,name='event_edit_media_form_tab'),
    #Event graphics tab page
    path('event_details/<int:event_id>/edit/graphics',views.event_edit_graphics_form_tab,name='event_edit_graphics_form_tab'),
    #Event graphics links sub tab page
    path('event_details/<int:event_id>/edit/graphics/links',views.event_edit_graphics_form_links_sub_tab,name='event_edit_graphics_form_links_sub_tab'),
    #Event content tab page
    path('event_details/<int:event_id>/edit/content',views.event_edit_content_form_tab,name='event_edit_content_form_tab'),
    #Super Event Creation Form
    path('events/create_super_event/',views.super_event_creation,name="super_event_creation"), 
    #Event preview
    path('event_details/<int:event_id>/preview/',views.event_preview,name='event_preview'),  

]