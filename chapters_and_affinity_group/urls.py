from django.urls import path
from . import views

app_name="chapters_and_affinity_group"

urlpatterns = [
    
    path('sc_ag_renewal_stats/',views.get_sc_ag_renewal_stats,name="sc_ag_renewal_stats"),
    path('<str:primary>/',views.sc_ag_homepage,name='sc_ag_homepage'),
    # For SC AG Members
    path('<str:primary>/members',views.sc_ag_members,name='sc_ag_members'),
    
    # For SC AG Panels
    path('<str:primary>/panels',views.sc_ag_panels,name="sc_ag_panels"),
    path('<str:primary>/panels/<str:panel_pk>',views.sc_ag_panel_details,name="sc_ag_panel_details"),
    path('<str:primary>/panels/<str:panel_pk>/officers',views.sc_ag_panel_details_officers_tab,name="sc_ag_panel_details_officers"),
    path('<str:primary>/panels/<str:panel_pk>/volunteers',views.sc_ag_panel_details_volunteers_tab,name="sc_ag_panel_details_volunteers"),
    path('<str:primary>/panels/<str:panel_pk>/alumni',views.sc_ag_panel_details_alumni_members_tab,name="sc_ag_panel_details_alumni"),
    
    # For SC AG Renewals
    path('<str:primary>/membership_renewal',views.sc_ag_membership_renewal_sessions,name="sc_ag_membership_renewal"),
    path('<str:primary>/membership_renewal/<str:renewal_session>/requests',views.sc_ag_renewal_session_details,name="sc_ag_membership_renewal_details"),
    path('<str:primary>/sc_ag_renewal_excel_sheet/<str:renewal_session>',views.sc_ag_renewal_excel_sheet,name="generate_sc_ag_renewal_excel"),
    
    # For SC AG Data Access
    path('<str:primary>/manage_access',views.sc_ag_manage_access,name="sc_ag_manage_access"),
    
    # for SC AG Events
    path('<str:primary>/events/',views.event_control_homepage,name="event_control_homepage"),
    path('<str:primary>/events/<int:event_id>',views.event_description,name='event_dashboard'),
    path('<str:primary>/events/create_event/',views.event_creation_form_page,name='event_creation_form1'),
    path('<str:primary>/events/create_event/<int:event_id>/page-p2', views.event_creation_form_page2, name="event_creation_form2"),
    path('<str:primary>/events/create_event/<int:event_id>/page-p3', views.event_creation_form_page3, name="event_creation_form3"),
    path('<str:primary>/events/create_super_event/',views.super_event_creation,name="super_event_creation"),    

]
