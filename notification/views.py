from django.shortcuts import render, redirect
from django.db import DatabaseError, IntegrityError, InternalError
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponse,JsonResponse
from django.views import View
from insb_port import settings
from notification.models import MemberNotifications
from notification.notifications import NotificationHandler
from port.renderData import PortData
from recruitment.models import recruitment_session, recruited_members
import users
from users.models import Members
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
from django.core.exceptions import ObjectDoesNotExist
import xlwt,csv
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
        has_access=(Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username))
        if True:
            
            try:
                member_notifications = MemberNotifications.objects.filter(member=Members.objects.get(ieee_id=request.user.username)).order_by('-notification__timestamp')
            except:
                member_notifications = None
            
            context={
                'all_sc_ag':sc_ag,
                "user_data":user_data,
                'member_notifications':member_notifications,
                'media_url':settings.MEDIA_URL
            }

            return render(request, 'notification.html', context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    
    
class MarkNotificationAsReadAjax(View):
    def get(self,request):
        member_notification_id = request.GET.get('member_notification_id')
        try:
            NotificationHandler.mark_as_read(member_notification_id)
            return JsonResponse('Success', safe=False)
        except:
            return JsonResponse('Something went wrong!',safe=False)
        
class MarkNotificationAsUnReadAjax(View):
    def get(self,request):
        member_notification_id = request.GET.get('member_notification_id')
        try:
            NotificationHandler.mark_as_unread(member_notification_id)
            return JsonResponse('Success', safe=False)
        except:
            return JsonResponse('Something went wrong!',safe=False)
        
class DeleteNotifcationUserAjax(View):
    def get(self,request, *args, **kwargs):
        member_notification_id = request.GET.get('member_notification_id')
        try:
            if NotificationHandler.delete_member_notification(request,member_notification_id):
                message = "Notifcation deleted!"
                return JsonResponse({'message': message,'deleted':True}, status=200)
            else:
                message = "Task not yet completed, you can't delete this notification!"
                return JsonResponse({'message': message,'deleted':False}, status=200)     
        except:
            return JsonResponse('Something went wrong!',safe=False)