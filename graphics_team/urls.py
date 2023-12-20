from django.urls import path,include
from . import views

app_name="graphics_team"

urlpatterns = [
    path('',views.team_homepage,name="team_homepage"),
    #Manage Team
    path('manage_team/',views.manage_team,name="manage_team"),
    #Event page
    path('event_page/',views.event_page,name="event_page"),
    #Event form
    path('event_page/<int:event_id>',views.event_form,name="event_form"),
<<<<<<< HEAD
    path('event_page/<int:event_id>',views.graphics_form_add_notes,name="event_form"),
    path('event_page/<int:event_id>/add_links',views.graphics_form_add_notes,name="add_links_event_form"),
=======
    path('event_page/<int:event_id>/add_links',views.event_form_add_notes,name="add_link_event_form"),


>>>>>>> 47f8c109133e1f8c98ee0995de78018e1cae2e37
]


