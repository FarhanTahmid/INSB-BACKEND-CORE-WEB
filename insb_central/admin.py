from django.contrib import admin
from . models import Events,Permission_criteria
# Register your models here.

#Creating customized View For DJANGO Admin
@admin.register(Events)
class Events(admin.ModelAdmin):
    list_display=['id','event_name','final_date'] 
@admin.register(Permission_criteria)
class Permission_Category(admin.ModelAdmin):
    list_display=['id','permission_name','template']
