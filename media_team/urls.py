from django.urls import path,include
from . import views
from central_branch.views import task_edit,add_task,create_task,upload_task

app_name="media_team"

urlpatterns = [
    path('',views.team_homepage,name="team_homepage"),
    #Manage Team
    path('manage_team/',views.manage_team,name="manage_team"),
    #Event page
    path('event_page/',views.event_page,name="event_page"),
    #Event Form
    path('event_page/<int:event_id>',views.event_form,name="event_form"),
    #Task pages
    path('task_home/',views.task_home,name="task_home"),
    path('<int:team_primary>/task/create_task',create_task,name="create_task"),
    path('task/<int:task_id>',task_edit,name="task_edit"),
    path('<int:team_primary>/task/<int:task_id>',task_edit,name="team_task_edit"),
    path('task/<int:task_id>/add_task/',add_task,name="add_task"),
    path('<int:team_primary>/task/<int:task_id>/add_task/',add_task,name="team_add_task"),
    path('task/<int:team_primary>/<int:task_id>/upload_task/',upload_task,name="upload_task"),


]
