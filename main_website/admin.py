from django.contrib import admin
from .models import Research_Papers,Blog_Category,Blog,IEEE_Bangladesh_Section,IEEE_Bangladesh_Section_Gallery
# Register your models here.
###Society AGS###
# RAS
from ieee_nsu_sb_ras_sbc.models import Ras_Sbc
@admin.register(Ras_Sbc)
class Ras_Sbc(admin.ModelAdmin):
    list_display=['id']

#Research Blogs Category
@admin.register(Research_Papers)
class ResearchPaper(admin.ModelAdmin):
    list_display = ['id','title','author_names','research_banner_picture','publication_link']
@admin.register(Blog_Category)
class Blog_Category(admin.ModelAdmin):
    list_display=['id','blog_category']
@admin.register(Blog)
class Blog(admin.ModelAdmin):
    list_display=['id','writer_name','title','date']
    

#Homepage Models
from . models import HomePageTopBanner
@admin.register(HomePageTopBanner)
class HomepageBannerData(admin.ModelAdmin):
    list_display=['id']

#Homepage Ribbon Picture
from . models import BannerPictureWithStat
@admin.register(BannerPictureWithStat)
class RibbonPicture(admin.ModelAdmin):
    list_display=['id']
    
# Achievements
from .models import Achievements
@admin.register(Achievements)
class Achievements(admin.ModelAdmin):
    list_display=['id','award_name','award_of']

@admin.register(IEEE_Bangladesh_Section)
class IEEE_Bangladesh_Section_Admin(admin.ModelAdmin):

    list_display = ['about_ieee_bangladesh','ieee_bangladesh_logo','member_and_volunteer_description','member_and_volunteer_picture','benefits_description','student_branches_description','affinity_groups_description','community_and_society_description',]
    
@admin.register(IEEE_Bangladesh_Section_Gallery)
class IEEE_Bangldesh_Section_Gallery(admin.ModelAdmin):

    list_display=['picture']
