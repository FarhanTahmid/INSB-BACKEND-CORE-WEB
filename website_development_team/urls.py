from django.urls import path,include
from . import views
from central_branch.views import task_edit,add_task,create_task,upload_task,task_home

app_name="website_development_team"

urlpatterns = [
    path('',views.team_homepage,name="team_homepage"),
    #Manage Team
    path('manage_team/',views.manage_team,name="manage_team"),
    
    #Task
    path('<int:team_primary>/create_task/',create_task,name="create_task_team"),
    path('<int:team_primary>/task_home/',task_home,name="task_home_team"),
]
