from django.contrib import admin

from port.forms import Chapter_Society_Affinity_Groups_Form
from . models import Teams,Roles_and_Position,Chapters_Society_and_Affinity_Groups
# Register your models here.
@admin.register(Teams)
class Teams(admin.ModelAdmin):
    list_display=['id','team_name','team_of','primary','completed_task_points']
@admin.register(Roles_and_Position)
class Roles(admin.ModelAdmin):
    list_display= ['id','role','role_of','rank','is_eb_member','is_mentor','is_sc_ag_eb_member','is_officer','is_co_ordinator','is_faculty','is_volunteer','is_core_volunteer']
@admin.register(Chapters_Society_and_Affinity_Groups)
class Chapter_Society(admin.ModelAdmin):
    form = Chapter_Society_Affinity_Groups_Form
    list_display=['id','group_name','primary','short_form','primary_color_code','secondary_color_code','mission_vision_color_code','text_color_code','logo','short_form_2','page_title','secondary_paragraph','about_description',
                  'background_image','mission_description','mission_picture',
                  'vision_description','vision_picture','what_is_this_description','why_join_it',
                  'what_activites_it_has','how_to_join','email','facebook_link']
    
from .models import *  
@admin.register(Panels)
class Panels(admin.ModelAdmin):
    list_display=[
        'year','creation_time','current','panel_of'
    ]

@admin.register(VolunteerAwards)
class All_Awards(admin.ModelAdmin):
    list_display=[
        'volunteer_award_name','award_of','panel'
    ]

@admin.register(SkillSetTypes)
class SkillSetTypes(admin.ModelAdmin):
    list_display=[
        'pk','skill_type'
    ]