from django.urls import path,include
from . import views

app_name = "content_writing_and_publications_team"

urlpatterns = [
    path('',views.homepage,name="team_homepage"),
    #Manage Team
    path('manage_team/',views.manage_team,name="manage_team")
]
