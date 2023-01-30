from django.contrib import admin
from . models import team_meeting_minutes
# Register your models here.
@admin.register(team_meeting_minutes)
class team_meeting_minutes(admin.ModelAdmin):
    list_display=['id','team_id','meeting_title']