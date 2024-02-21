from django.contrib import admin
from .models import Task_Category, Task

# Register your models here.
@admin.register(Task_Category)
class Task_Category(admin.ModelAdmin):
    list_display = ['name', 'points']

@admin.register(Task)
class Task(admin.ModelAdmin):
    list_display = ['id','title','task_category','task_type','sc_ag_id','deadline','has_file_upload','has_content','has_picture_upload','has_permission_paper']
