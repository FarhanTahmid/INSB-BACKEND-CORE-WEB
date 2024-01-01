from django.contrib import admin
from . models import Members,Alumni_Members,ResetPasswordTokenTable,User_IP_Address

# Register your models here.
@admin.register(Members)
class Members(admin.ModelAdmin):
    list_display=['ieee_id','name','gender','email_ieee','team','position','facebook_url','email_nsu','is_active_member']

@admin.register(Alumni_Members)
class Alumni_Members(admin.ModelAdmin):
    list_display=[
        'name'
    ]


from . models import Panel_Members
@admin.register(Panel_Members)
class PanelMembers(admin.ModelAdmin):
    list_display=[
        'member','ex_member','tenure','position','team'
    ]

@admin.register(ResetPasswordTokenTable)
class ResetPasswordTokenTable(admin.ModelAdmin):
    list_display=[
        'user','token'
    ]
@admin.register(User_IP_Address)
class User(admin.ModelAdmin):
    list_display = ['ip_address','created_at']