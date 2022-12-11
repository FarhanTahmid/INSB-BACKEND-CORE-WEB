import imp
from django.urls import path,include
from . import views

app_name='users'

##defining the urls to work with

urlpatterns = [
   path('',views.md_team_homepage,name="md_team_homepage"),
   path('members/',views.members_list,name="members_list"),
   path('export_excel',views.generateExcelSheet,name="export_excel"),
   path('membership_renewal/',views.membership_renewal,name="membership_renewal"),
   path('membership_renewal/session/<str:pk>',views.renewal_session_data,name="renewal_session_data"),
   path('renewal_form/<str:pk>',views.membership_renewal_form,name="renewal_form"),
   path('renewal_request/<str:pk>/<str:name>',views.renewal_request_details,name="request_details"),
   
]
