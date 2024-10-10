from django.urls import path,include
from . import views
from central_branch.views import task_edit,add_task,create_task,upload_task,task_home

app_name='events_and_management_team'

urlpatterns = [
    path('',views.em_team_homepage,name="em_team_homepage"),
    path('emt_data_access/',views.emt_data_access,name="emt_data_access"),
    path('emt_task_assign/',views.emt_task_assign,name="emt_task_assign"),

    #Task
    path('create_task/<int:team_primary>/',create_task,name="create_task_team"),
    path('task_home/<int:team_primary>/',task_home,name="task_home_team"),
    path('task/<int:task_id>/<int:team_primary>/',task_edit,name="task_edit_team"),
    path('task/<int:task_id>/upload_task/<int:team_primary>/',upload_task,name="upload_task_team"),
    path('task/<int:task_id>/add_task/<int:team_primary>/<int:by_coordinators>/',add_task,name="add_task_team"),
]
