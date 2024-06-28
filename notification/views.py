from django.shortcuts import render, redirect
from django.db import DatabaseError, IntegrityError, InternalError
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponse,JsonResponse
from django.views import View
from insb_port import settings
from notification.models import MemberNotifications
from notification.notifications import NotificationHandler
from port.renderData import PortData
from recruitment.models import recruitment_session, recruited_members
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
from . import push_notification
from users.renderData import LoggedinUser

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
        print(member_notification_id)
        print("Mark as read")
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

class ReceiveTokenAjax(View):
    def get(self,request, *args, **kwargs):
        token = request.GET.get('token')
        try:
            member = Members.objects.get(ieee_id=request.user.username)
            member_notifications_count = MemberNotifications.objects.filter(member=member,is_read = False).order_by('-notification__timestamp').count()
            # Send the push notification
            if push_notification.save_token(member,token):
                print("returned from token function")

            ##sending a push notification once user lands on page (optional)
            if member_notifications_count > 0:
                title = "IEEE NSU SB PORTAL"
                body = f"You have {str(member_notifications_count)} new notifications!"
                response = push_notification.send_push_notification(title,body,token)   
                return JsonResponse('Message sent!',response)  
            else:
                return JsonResponse('No message to send!',safe=False)
        except:
            return JsonResponse('Something went wrong!',safe=False)

@login_required
def fetch_notifications(request):
    try:
        member = Members.objects.get(ieee_id=request.user.username)
        member_notifications = MemberNotifications.objects.filter(member=member,is_read = False).order_by('-notification__timestamp')
    except:
        member_notifications = None
    notifications = []
    if member_notifications == None:
        notifications = []
    else:
        for member_notification in member_notifications:
            
            try:
                profile_picture = member_notification.notification.created_by.user_profile_picture
            except:
                profile_picture = 'default_profile_picture.png'
            dic = {
                'id': member_notification.pk,
                'inside_link': member_notification.notification.inside_link,
                'general_message': member_notification.notification.general_message,
                'timestamp': member_notification.notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'created_by': {
                    # 'profile_picture': profile_picture
                                        
                },
                'is_read': member_notification.is_read,
            }
       
            notifications.append(dic)
    
    return JsonResponse({'notifications': notifications})

