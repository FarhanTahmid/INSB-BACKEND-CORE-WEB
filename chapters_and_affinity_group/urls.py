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
    path('<str:primary>/events/create_event/',views.event_creation_form_page,name='event_creation_form1'),
    path('<str:primary>/events/create_event/<int:event_id>/page-2', views.event_creation_form_page2, name="event_creation_form2"),
    path('<str:primary>/events/create_event/<int:event_id>/page-3', views.event_creation_form_page3, name="event_creation_form3"),
    path('<str:primary>/event_details/<int:event_id>/edit/',views.event_edit_form,name='event_edit_form'),
    #Event media tab page
    path('<str:primary>/event_details/<int:event_id>/edit/media',views.event_edit_media_form_tab,name='event_edit_media_form_tab'),
    #Event graphics tab page
    path('<str:primary>/event_details/<int:event_id>/edit/graphics',views.event_edit_graphics_form_tab,name='event_edit_graphics_form_tab'),
    #Event graphics links sub tab page
    path('<str:primary>/event_details/<int:event_id>/edit/graphics/links',views.event_edit_graphics_form_links_sub_tab,name='event_edit_graphics_form_links_sub_tab'),
    #Event content tab page
    path('<str:primary>/event_details/<int:event_id>/edit/content',views.event_edit_content_form_tab,name='event_edit_content_form_tab'),
    #Event preview
    path('<str:primary>/event_details/<int:event_id>/preview/',views.event_preview,name='event_preview'),
    #Event Feedback
    path('<str:primary>/event_details/<int:event_id>/feedbacks/',views.event_feedback,name='event_feedback'),
    #Manage Main Website
    path('<str:primary>/manage_main_website',views.manage_main_website,name="manage_main_website"),
    #Manage Main Website Preview
    path('<str:primary>/manage_main_website/preview',views.manage_main_website_preview,name="manage_main_website_preview"), 
    #Feed Back
    path('<str:primary>/feedbacks',views.feedbacks,name="feedbacks"),
    #Mega Event Creation Form
    path('<str:primary>/events/create_mega_event/',views.mega_event_creation,name="mega_event_creation"), 
    #Mega Events homepage
    path('<str:primary>/events/mega_events/',views.mega_events,name="mega_events"), 
    #Mega Events edit
    path('<str:primary>/events/mega_event_edit/<int:mega_event_id>/',views.mega_event_edit,name="mega_event_edit"), 
    #Add Events to Mega Event
    path('<str:primary>/events/mega_event_add_event/<int:mega_event_id>/',views.mega_event_add_event,name="mega_event_add_event"), 
]
