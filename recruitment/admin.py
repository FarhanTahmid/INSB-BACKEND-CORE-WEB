from django.contrib import admin
from . models import recruitment_session,recruited_members
# Register your models here.

@admin.register(recruitment_session)
class Session(admin.ModelAdmin):
    list_display= ['id','session']
@admin.register(recruited_members)
class Recruited_Members(admin.ModelAdmin):
    list_display=['nsu_id','email_personal']
