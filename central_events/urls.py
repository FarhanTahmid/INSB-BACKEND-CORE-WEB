from django.urls import path,include
from . import views

app_name='central_events'

urlpatterns = [
    #Event control page 
    path('event_control',views.event_control_homepage, name='event_control'),
    #Event Creation Form page 1
    path('create_event/',views.event_creation_form_page,name='event_creation_form1'),
    #Event Creation Form Page 2
    path("create_event/<int:event_id>/page-p2", views.event_creation_form_page2, name="event_creation_form2"),
    #Event creation page 3
    path("create_event/<int:event_id>/page-3", views.event_creation_form_page3, name="event_creation_form3"),
    #Super Event Creation Form
    path('create_super_event/',views.super_event_creation,name="super_event_creation"),
    #event dashboard team
    path('event_details/<int:event_id>',views.event_description,name='event_dashboard'),
]