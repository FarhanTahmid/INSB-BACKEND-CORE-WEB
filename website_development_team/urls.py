from django.urls import path,include
from . import views

app_name="website_development_team"

urlpatterns = [
    path('',views.team_homepage,name="team_homepage"),
    #Manage Team
    path('manage_team/',views.manage_team,name="manage_team"),
    #Task page
    path('task_home/',views.task_home,name="task_home"),
    path('task/<int:task_id>',views.task_edit,name="task_edit"),
    path('task/<int:task_id>/add_task/',views.add_task,name="add_task"),
]
