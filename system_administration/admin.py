from django.contrib import admin
from . models import adminUsers,MDT_Data_Access,Developer_criteria,Project_Developers,Project_leads
# Register your models here.
@admin.register(adminUsers)
class Admin(admin.ModelAdmin):
    list_display=['username','name','email']

@admin.register(MDT_Data_Access)
class Access_Criteria(admin.ModelAdmin):
    list_display=['ieee_id']

@admin.register(Developer_criteria)
class Developer_Criteria(admin.ModelAdmin):
    list_display=['id','developer_type']

@admin.register(Project_leads)
class Project_leads(admin.ModelAdmin):
    list_display=['name','developer_type']

@admin.register(Project_Developers)
class Project_Developer(admin.ModelAdmin):
    list_display=['name','developer_type']