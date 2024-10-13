from django.urls import path,include
from . import views
from central_branch.views import task_edit,add_task,create_task,upload_task,task_home,forward_to_incharges

app_name = "content_writing_and_publications_team"

urlpatterns = [
    path('',views.homepage,name="team_homepage"),
    #Manage Team
    path('manage_team/',views.manage_team,name="manage_team"),
    path('event_page/',views.event_page,name="event_page"),
    path('event_page/<int:event_id>',views.event_form,name="event_form"),
    path('event_page/<int:event_id>/add_notes/',views.event_form_add_notes,name="event_form_add_notes"),
    path('content_page/',views.content_page,name="content_page"),
    path('create_content_form/',views.create_content_form,name="create_content_form"),
    path('content/<int:content_id>',views.content_edit,name="content_edit"),
    path('content/<int:content_id>/add_captions/',views.edit_content_form_add_notes,name="edit_content_form_add_notes"),

    #Task
    path('create_task/<int:team_primary>/',create_task,name="create_task_team"),
    path('task_home/<int:team_primary>/',task_home,name="task_home_team"),
    path('task/<int:task_id>/<int:team_primary>/',task_edit,name="task_edit_team"),
    path('task/<int:task_id>/upload_task/<int:team_primary>/',upload_task,name="upload_task_team"),
    path('task/<int:task_id>/forward_to_incharges/<int:team_primary>/',forward_to_incharges,name="forward_to_incharges"),
    path('task/<int:task_id>/add_task/<int:team_primary>/<int:by_coordinators>/',add_task,name="add_task_team"),
]