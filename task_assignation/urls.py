from django.urls import path
from . import views

app_name = 'task_assignation'

urlpatterns = [
        #task assignation
        path('',views.task_homepage, name='task_homepage'),
        path('',views.task_home, name='task_home'),
]
