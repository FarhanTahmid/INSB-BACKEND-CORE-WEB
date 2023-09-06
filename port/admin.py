from django.contrib import admin
from . models import Teams,Roles_and_Position,Chapters_Society_and_Affinity_Groups,Society_Chapters_AG_Roles_and_Positions,Society_Chapters_AG_Teams
# Register your models here.
@admin.register(Teams)
class Teams(admin.ModelAdmin):
    list_display=['id','team_name','primary']
@admin.register(Roles_and_Position)
class Roles(admin.ModelAdmin):
    list_display= ['id','role','is_eb_member','is_officer','is_faculty']
@admin.register(Chapters_Society_and_Affinity_Groups)
class Chapter_Society(admin.ModelAdmin):
    list_display=['id','group_name','primary']

@admin.register(Society_Chapters_AG_Roles_and_Positions)
class Society_Chapter_Roles(admin.ModelAdmin):
    list_display=[
        'id','chapter_id','position_name','is_faculty_position','is_eb_position','is_officer_position'
    ]

@admin.register(Society_Chapters_AG_Teams)
class Society_Chapter_Teams(admin.ModelAdmin):
    list_display = ['id','chapter_id','team_name']
