from django.contrib import messages
import logging,traceback
from system_administration.system_error_handling import ErrorHandling
from main_website.models import *
from port.models import *
from users. models import *


class MainWebsiteRenderData:
    def add_awards(request):
        logger=logging.getLogger(__name__)
        
        try:
            # create new Achievement
            new_achivement=Achievements.objects.create(
                award_name=request.POST['award_name'],
                award_description=request.POST['award_description'],
                award_winning_year=request.POST['award_winning_year'],
                award_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=request.POST.get('award_of')),
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

    def get_all_achievements(request):
        try:
            # load all achievements
            all_achievements=Achievements.objects.all().order_by('award_winning_year')
            return all_achievements
        except Exception as e:
            MainWebsiteRenderData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not load Achievements. Something went wrong!")
        