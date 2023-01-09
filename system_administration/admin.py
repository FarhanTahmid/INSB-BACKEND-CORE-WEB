from django.contrib import admin
from . models import adminUsers,MDT_Data_Access
# Register your models here.
@admin.register(adminUsers)
class Admin(admin.ModelAdmin):
    list_display=['username','name','email']

@admin.register(MDT_Data_Access)
class Access_Criteria(admin.ModelAdmin):
    list_display=['ieee_id']