from django.contrib import admin
from . models import adminUsers,Access_Criterias,Team_Data_Access
# Register your models here.
@admin.register(adminUsers)
class Admin(admin.ModelAdmin):
    list_display=['username','name','email']
@admin.register(Access_Criterias)
class Access_Criteria(admin.ModelAdmin):
    list_display=['id','criteria_name']
@admin.register(Team_Data_Access)
class Access_Criteria(admin.ModelAdmin):
    list_display=['ieee_id','team','criteria','has_permission']