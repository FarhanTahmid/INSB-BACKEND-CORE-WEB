from django.contrib import admin
from . models import Members,Ex_panel_members,Executive_commitee,Executive_commitee_members,ResetPasswordTokenTable,User

# Register your models here.
@admin.register(Members)
class Members(admin.ModelAdmin):
    list_display=['ieee_id','name','gender','email_ieee','team','position','facebook_url','email_nsu']

@admin.register(Ex_panel_members)
class Ex_Panel_Members(admin.ModelAdmin):
    list_display=[
        'name'
    ]

@admin.register(Executive_commitee)
class Executive_Commitee(admin.ModelAdmin):
    list_display=[
        'year','current'
    ]

@admin.register(Executive_commitee_members)
class Executive_Commitee_members(admin.ModelAdmin):
    list_display=[
        'member','year','position'
    ]

@admin.register(ResetPasswordTokenTable)
class ResetPasswordTokenTable(admin.ModelAdmin):
    list_display=[
        'user','token'
    ]
@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ['ip_address','created_at']