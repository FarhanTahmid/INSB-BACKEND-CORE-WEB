from django.contrib import admin
from .models import Task_Category,Task,Task_Drive_Link,Task_Content,Task_Document,Task_Media

# Register your models here.
@admin.register(Task_Category)
class Task_Category(admin.ModelAdmin):
    list_display = ['name', 'points']

@admin.register(Task)
class Task(admin.ModelAdmin):
    list_display = ['id','title','task_category','task_type','task_of','deadline','has_drive_link','has_file_upload','has_content','has_picture_upload','has_permission_paper']

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
