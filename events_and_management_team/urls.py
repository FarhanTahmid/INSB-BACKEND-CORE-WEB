from django.urls import path,include
from . import views

app_name='events_and_management_team'

urlpatterns = [
    path('',views.em_team_homepage,name="em_team_homepage"),
    path('emt_data_access/',views.emt_data_access,name="emt_data_access"),
    path('emt_task_assign/',views.emt_task_assign,name="emt_task_assign")
]
