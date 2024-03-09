from django.contrib import admin
from .models import Task_Category,Task,Task_Drive_Link,Task_Content,Task_Document,Task_Media,Task_Log,Member_Task_Point,Team_Task_Point,Member_Task_Upload_Types,Permission_Paper

# Register your models here.
@admin.register(Task_Category)
class Task_Category(admin.ModelAdmin):
    list_display = ['name', 'points']

@admin.register(Task)
class Task(admin.ModelAdmin):
    list_display = ['id','title','task_category','task_type','task_of','task_created_by','deadline','is_task_completed','has_drive_link','has_file_upload','has_content','has_media','has_permission_paper','has_others']

@admin.register(Task_Drive_Link)
class Task_Drive_Link(admin.ModelAdmin):
    list_display = ['id','task','drive_link']

@admin.register(Task_Content)
class Task_Content(admin.ModelAdmin):
    list_display = ['id','task','content']

@admin.register(Task_Document)
class Task_Document(admin.ModelAdmin):
    list_display = ['id','task','document']

@admin.register(Task_Media)
class Task_Media(admin.ModelAdmin):
    list_display = ['id','task','media']

@admin.register(Task_Log)
class Task_Log(admin.ModelAdmin):
    list_display=[
        'task_number','task_log_details','update_task_number'
    ]

@admin.register(Member_Task_Point)
class Member_Task_Point(admin.ModelAdmin):
    list_display = ['member','task','completion_points','is_task_completed']

@admin.register(Team_Task_Point)
class Team_Task_Point(admin.ModelAdmin):
    list_display = ['team','task','completion_points','is_task_completed']

@admin.register(Member_Task_Upload_Types)
class Member_Task_Upload_Types(admin.ModelAdmin):
    list_display = [
        'task_member','task','has_drive_link','has_file_upload','has_content','has_media','has_permission_paper'
    ]
@admin.register(Permission_Paper)
class Permission_Paper(admin.ModelAdmin):
    list_display = [
        'task','permission_paper'
    ]