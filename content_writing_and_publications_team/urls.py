from django.urls import path,include
from . import views

app_name = "content_writing_and_publications_team"

urlpatterns = [
    path('',views.homepage,name="team_homepage"),
    #Manage Team
    path('manage_team/',views.manage_team,name="manage_team"),
    path('event_page/',views.event_page,name="event_page"),
    path('event_page/<int:event_id>',views.event_form,name="event_form"),
    path('event_page/<int:event_id>/add_notes',views.event_form_add_notes,name="event_form_add_notes"),
]
