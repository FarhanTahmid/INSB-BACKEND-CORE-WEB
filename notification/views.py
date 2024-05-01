from django.shortcuts import render, redirect
from django.db import DatabaseError, IntegrityError, InternalError
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponse,JsonResponse
from port.renderData import PortData
from recruitment.models import recruitment_session, recruited_members
import users
from users.models import MemberSkillSets, Members
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
from django.core.exceptions import ObjectDoesNotExist
import xlwt,csv
from django.db.utils import IntegrityError
from membership_development_team.renderData import MDT_DATA
from membership_development_team import email_sending
from system_administration.render_access import Access_Render
from users.renderData import LoggedinUser,member_login_permission
import logging
from system_administration.system_error_handling import ErrorHandling
from datetime import datetime
import traceback
from central_branch import views as cv

# Create your views here.
logger=logging.getLogger(__name__)

@login_required
@member_login_permission
def notification(request):
    '''Loads all the recruitment sessions present in the database
        this can also register a recruitment session upon data entry
        this passes all the datas into the template file    
    '''
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        #Checking user access
        user=request.user
        has_access=(MDT_DATA.recruitment_session_view_access_control(user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username))
        if has_access:
            
            if request.method == "POST":
                session_name = request.POST["recruitment_session"]
                session_time=datetime.now()
                try:
                    add_session = recruitment_session(session=session_name,session_time=session_time)
                    add_session.save()
                except DatabaseError:
                    return DatabaseError
            
            context={
                'all_sc_ag':sc_ag,
                "user_data":user_data
            }

            return render(request, 'notification.html', context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)