from django.urls import path
from . import views

app_name = 'task_assignation'

urlpatterns = [
        #task assignation
        path('',views.create_task, name='create_task'),
        path('',views.task_home, name='task_home'),
]
