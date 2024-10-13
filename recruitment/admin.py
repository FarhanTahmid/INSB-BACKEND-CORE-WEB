from django.contrib import admin
from . models import recruitment_session,recruited_members,nsu_school,nsu_departments,nsu_majors
# Register your models here.

@admin.register(recruitment_session)
class Session(admin.ModelAdmin):
    list_display= ['id','session','session_time']
@admin.register(recruited_members)
class Recruited_Members(admin.ModelAdmin):
    list_display=['nsu_id','first_name','email_personal','ieee_payment_status']
@admin.register(nsu_school)
class NSU_Schools(admin.ModelAdmin):
    list_display=['school_full_name','school_initial']
@admin.register(nsu_departments)
class NSU_Departments(admin.ModelAdmin):
    list_display = ['department_of','department_full_name','department_initial']
@admin.register(nsu_majors)
class NSU_Majors(admin.ModelAdmin):
    list_display = ['major_of','major_full_name','major_initial']
