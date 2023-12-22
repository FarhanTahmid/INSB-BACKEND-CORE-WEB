from django.contrib import messages
import logging,traceback
from system_administration.system_error_handling import ErrorHandling
from main_website.models import *
from port.models import *
from users. models import *
import os

class MainWebsiteRenderData:
    logger=logging.getLogger(__name__)
    
    def add_awards(request):
        # get the sc_ag
        get_sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(pk=request.POST.get('award_of'))
        try:
            # create new Achievement
            new_achivement=Achievements.objects.create(
                award_name=request.POST['award_name'],
                award_description=request.POST['award_description'],
                award_winning_year=request.POST['award_winning_year'],
                award_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=get_sc_ag.primary),
                award_picture=request.FILES.get('award_picture')
            )        
            new_achivement.save()
            messages.success(request,"New Achievement Created!")
            return True
        except Exception as e:
            MainWebsiteRenderData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not add Achievements. Something went wrong!")
            return False
    
    def delete_achievement(request):
        try:
            # get the achievement
            achivement = Achievements.objects.get(pk=request.POST["remove_achievement"])
            # delete its picture from filepath
            if(os.path.isfile(achivement.award_picture.path)):
                os.remove(achivement.award_picture.path)
            achivement.delete()
            messages.info(request,"An item was deleted!")
            return True
        except Exception as e:
            MainWebsiteRenderData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not Delete item. Something went wrong!")
            return False
       
    def get_all_achievements(request):
        try:
            # load all achievements
            all_achievements=Achievements.objects.all().order_by('-award_winning_year')
            return all_achievements
        except Exception as e:
            MainWebsiteRenderData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not load Achievements. Something went wrong!")
    
    def delete_blog(request):
        try:
            get_the_blog=Blog.objects.get(pk=request.POST['blog_pk'])
            if(os.path.isfile(get_the_blog.blog_banner_picture.path)):
                os.remove(get_the_blog.blog_banner_picture.path)
            get_the_blog.delete()
            messages.info(request,'A blog was deleted!')
        except Exception as e:
            MainWebsiteRenderData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not delete Blogs. Something went wrong!")
    
    def delete_research_paper(request):
        try:
            get_the_paper=Research_Papers.objects.get(pk=request.POST['research_pk'])
            if(os.path.isfile(get_the_paper.research_banner_picture.path)):
                os.remove(get_the_paper.research_banner_picture.path)
            get_the_paper.delete()
            messages.info(request,"A Research Paper was deleted!")
        except Exception as e:
            MainWebsiteRenderData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not delete Research Paper. Something went wrong!")

                     