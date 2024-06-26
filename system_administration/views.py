from django.shortcuts import render,redirect
from .render_access import Access_Render
from .models import system
import logging
from system_administration.system_error_handling import ErrorHandling
from datetime import datetime
import traceback
from central_branch import views as cv
# Create your views here.

logger=logging.getLogger(__name__)

def main_website_update_view(request):

    try:

        if(Access_Render.system_administrator_superuser_access(request.user.username) or Access_Render.system_administrator_staffuser_access(request.user.username)):
            return redirect('main_website:homepage')
        if(system.objects.filter(main_website_under_maintenance=False).first()):
            return redirect('main_website:homepage')
        else:    
            return render(request,'main_web_update_view.html')
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    
def restriction(request):
    return render(request,"notification_restriction_page.html")