from django.shortcuts import render,redirect
from system_administration.models import Project_leads,Project_Developers
from django.conf import settings
import traceback
import logging
from system_administration.system_error_handling import ErrorHandling
from datetime import datetime
from central_branch import views as cv

logger=logging.getLogger(__name__)


# Create your views here.
def homepage(request):

    try:
        #check if user is already logged in
        user=request.user
        if (user.is_authenticated):
            return redirect('users:dashboard')
        else:
            return render(request,'port/landing_page.html')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def developed_by(request):
    '''This function loads and shows all the developers for the site'''

    try:

        #load leads and the developers of the project
        project_leads=Project_leads.objects.all()
        project_developers=Project_Developers.objects.all().order_by('-reputation_point')
        print(settings.MEDIA_URL)
        print(project_developers[0].developers_picture)
        
        context={
            'project_leads':project_leads,
            'project_developers':project_developers,
            'media':settings.MEDIA_URL
        }
        return render(request,'port/developer_intro.html',context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)