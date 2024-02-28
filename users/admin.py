from django.contrib import admin
from . models import Members,Alumni_Members,ResetPasswordTokenTable,User_IP_Address,UserSignupTokenTable,MemberSkillSets

# Register your models here.
@admin.register(Members)
class Members(admin.ModelAdmin):
    list_display=['ieee_id','name','gender','email_ieee','team','position','facebook_url','email_nsu','is_active_member','user_profile_picture','is_blocked']
    ordering = ['position__rank']
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
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(tenure__current=True).order_by("position__rank")
        return qs

@admin.register(ResetPasswordTokenTable)
class ResetPasswordTokenTable(admin.ModelAdmin):
    list_display=[
        'user','token'
    ]
@admin.register(User_IP_Address)
class User(admin.ModelAdmin):
    list_display = ['ip_address','created_at']

@admin.register(UserSignupTokenTable)
class UserSignupTokens(admin.ModelAdmin):
    list_display=['user','token']

from .models import VolunteerAwardRecievers
@admin.register(VolunteerAwardRecievers)
class Award_Recievers(admin.ModelAdmin):
    list_display=[
        'award_reciever','award'
    ]

@admin.register(MemberSkillSets)
class MemberSkillSets(admin.ModelAdmin):
    list_display=[
        'pk','member','skills'
    ]

    def skills(self, obj):
        return ", ".join([p.skill_type for p in obj.skill.all()])