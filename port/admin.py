from django.contrib import admin
from . models import Teams,Roles_and_Position,Chapters_Society_and_Affinity_Groups
# Register your models here.
@admin.register(Teams)
class Teams(admin.ModelAdmin):
    list_display=['id','team_name','team_of','primary']
@admin.register(Roles_and_Position)
class Roles(admin.ModelAdmin):
    list_display= ['id','role','role_of','is_eb_member','is_mentor','is_sc_ag_eb_member','is_officer','is_co_ordinator','is_faculty','is_volunteer','is_core_volunteer']
@admin.register(Chapters_Society_and_Affinity_Groups)
class Chapter_Society(admin.ModelAdmin):
    list_display=['id','group_name','primary','short_form','about_description',
                  'sc_ag_logo','background_image','mission_description','mission_picture',
                  'vision_description','vision_picture','what_is_this_description','why_join_it',
                  'what_activites_it_has','how_to_join','contact_name','contact_email','contact_messages']
    
from .models import Panels  
@admin.register(Panels)
class Panels(admin.ModelAdmin):
    list_display=[
        'year','creation_time','current','panel_of'
    ]

