from django.urls import path
from . import views

app_name="chapters_and_affinity_group"

urlpatterns = [
    path('<str:primary>/',views.sc_ag_homepage,name='sc_ag_homepage'),
    path('<str:primary>/members',views.sc_ag_members,name='sc_ag_members'),
    path('<str:primary>/panels',views.sc_ag_panels,name="sc_ag_panels"),
    path('<str:primary>/panels/<str:panel_pk>',views.sc_ag_panel_details,name="sc_ag_panel_details"),
]
