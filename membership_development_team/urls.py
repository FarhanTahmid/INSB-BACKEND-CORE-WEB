import imp
from django.urls import path,include
from . import views

app_name='membership_development_team'

##defining the urls to work with

urlpatterns = [
   path('',views.md_team_homepage,name="md_team_homepage"),
   path('members/',views.insb_members_list,name="members_list"),
   path('member_details/<int:ieee_id>',views.member_details,name="member_details"),
   path('export_excel',views.generateExcelSheet_membersList,name="export_excel"),
   path('membership_renewal/',views.membership_renewal,name="membership_renewal"),
   path('membership_renewal/session/<str:pk>',views.renewal_session_data,name="renewal_session_data"),
   path('renewal_form/<str:pk>',views.membership_renewal_form,name="renewal_form"),
   path('renewal_request/<str:pk>/<str:request_id>',views.renewal_request_details,name="request_details"), #using renewal request tables primary key 'id' as url because its the only unique matter in renewal process as no ieee id could be used
   path('export_excel_renewal_request/<str:session_id>',views.generateExcelSheet_renewal_requestList,name="export_excel_renewal_request"), #generate excel for renewal request
   path('data_access',views.data_access,name="data_access"),
   
]
