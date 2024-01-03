from django.contrib import admin
from .models import Research_Papers,Blog_Category,Blog
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

from .models import Magazines
@admin.register(Magazines)
class Magazines(admin.ModelAdmin):
    list_display=['id','magazine_title']
