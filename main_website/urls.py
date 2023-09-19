from django.urls import path
from . import views

app_name = "main_website"

urlpatterns = [
    path('',views.homepage,name="homepage"),
    path('all-events/',views.All_Events,name='all-events'),
    path('events/<int:event_id>',views.Event_Details,name='event-details'),
    path('research-papers/',views.Research_Paper,name="research_papers"),
    path('ieeensu_ras_sbc/',views.rasPage,name="ras_home"),
    path('blogs/',views.Blogs,name="blogs"),
    path('blogs/<int:blog_id>',views.blog_Description,name="blog_description")
]
