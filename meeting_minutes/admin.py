from django.contrib import admin
from . models import team_meeting_minutes, branch_meeting_minutes
# Register your models here.
@admin.register(team_meeting_minutes)
class team_meeting_minutes(admin.ModelAdmin):
    list_display=['id','team_id','team_meeting_title']

@admin.register(branch_meeting_minutes)
class branch_meeting_minutes(admin.ModelAdmin):
    list_display=['id','branch_or_society_id','branch_or_society_meeting_title']
