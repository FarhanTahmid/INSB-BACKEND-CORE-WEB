from django.urls import path
from . import views

app_name="chapters_and_affinity_group"

urlpatterns = [
    path('<str:primary>/',views.sc_ag_homepage,name='sc_ag_homepage'),
    path('<str:primary>/members',views.sc_ag_members,name='sc_ag_members'),
    path('<str:primary>/panels',views.sc_ag_panels,name="sc_ag_panels"),
    path('<str:primary>/panels/<str:panel_pk>',views.sc_ag_panel_details,name="sc_ag_panel_details"),
    path('<str:primary>/panels/<str:panel_pk>/officers',views.sc_ag_panel_details_officers_tab,name="sc_ag_panel_details_officers"),
    path('<str:primary>/panels/<str:panel_pk>/volunteers',views.sc_ag_panel_details_volunteers_tab,name="sc_ag_panel_details_volunteers"),
    path('<str:primary>/panels/<str:panel_pk>/alumni',views.sc_ag_panel_details_alumni_members_tab,name="sc_ag_panel_details_alumni"),
    path('<str:primary>/events/',views.event_control_homepage,name="event_control_homepage")
    

]
