from django.urls import path
from . import views

app_name = "main_website"

urlpatterns = [
    path('',views.homepage,name="homepage"),
    
    #ACTIVITY URLS
    # Event
    path('events/',views.event_homepage,name="event_homepage"),
    
    #SOCIETY AG URLS
    path('ras_sbc/',views.rasPage,name="ras_home"),

    #Achievements
    path('achievements/',views.achievements,name="achievements"),
    
    # Members
    path('panels/',views.current_panel_members,name="panel_members"),
    path('panels/<str:year>',views.panel_members_page,name="panel_members_previous"),
    
    
]
