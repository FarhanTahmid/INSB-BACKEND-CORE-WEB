from .models import *
from datetime import datetime
from system_administration.system_error_handling import ErrorHandling
import logging
import traceback


class NotificationHandler:
    
    logger=logging.getLogger(__name__)

    def create_notification_type():
        pass
    
    def create_notifications(notification_type,general_message,inside_link,created_by,reciever_list):
        
        '''this function creates new notification instances, assigns new notifications to the users as well
                -notification_type: must be a pk of an NotificationTypes object
                -general_message: the message that will be shown in the notification as preview.
                -inside_link: the link that the user will be redirected to upon clicking the notification.
                -timestamp: the current timestamp of the server
                -created_by: must return the user id (IEEE ID) of the user
                -reciever_list: list of IEEE ID's to whom the notification will be assigned to.            
        '''
        
        '''At the first step, the function will create a new Object of Notifications'''
        
        # get the object of notification_type, the passed value of the notification type must be the pk of the object
        notification_type = NotificationTypes.objects.get(pk=notification_type)
        timestamp=datetime.now()
        
        try:
            # get the object of members, the passed value of created by must be an instance of Members
            created_by=Members.objects.get(ieee_id=created_by)
            
            # create new object of Notifications
            new_notification = Notifications.objects.create(
                type=notification_type,timestamp=timestamp,general_message=general_message,
                inside_link=inside_link,created_by=created_by
            )
            # save the new instance of notification
            new_notification.save()
                        
        except Exception as e:
            # if the members instance is not found, create it under admin privilege
            
            # create new object of Notifications without created_by option
            new_notification = Notifications.objects.create(
                type=notification_type,timestamp=timestamp,general_message=general_message,
                inside_link=inside_link
            )
            # save the new instance of notification
            new_notification.save()
        
        try:
            # now create the notification for all reciever_list
            for reciever in reciever_list:
                
                # get the reciever from Members with IEEE ID
                reciever = Members.objects.get(ieee_id=reciever)
                
                # create the notification for the reciever
                new_notification_for_reciever = MemberNotifications.objects.create(
                    notification=new_notification,member=reciever,is_read=False                    
                )
                # save the new instance of notification from every reciever
                new_notification_for_reciever.save()
                # Push notifications to user device and email from here
            return True
        
        except Exception as e:
            NotificationHandler.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
            
    
    
    def update_notification():
        pass
    
    def delete_notification():
        pass
    
    
