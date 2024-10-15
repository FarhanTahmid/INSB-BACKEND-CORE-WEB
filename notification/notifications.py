from .models import *
from datetime import datetime
from system_administration.system_error_handling import ErrorHandling
import logging
import traceback
from task_assignation.models import Task
from . import push_notification
from .models import *
class NotificationHandler:
    
    logger=logging.getLogger(__name__)

    try:
        custom_notification_type=NotificationTypes.objects.get(type="Custom Notification")
    except:
        custom_notification_type = None

    def create_notification_type(notification_type, image_icon=None):
        pass
    
    def create_notifications(notification_type,title,general_message,inside_link,created_by,reciever_list,notification_of,event=None):
        
        '''This function creates new notification instances, assigns new notifications to the users as well
                -`notification_type`: must be a pk of an NotificationTypes object
                -`general_message`: the message that will be shown in the notification as preview.
                -`inside_link`: the link that the user will be redirected to upon clicking the notification.
                -`timestamp`: the current timestamp of the server
                -`created_by`: must return the user id (IEEE ID) of the user
                -`reciever_list`: list of IEEE ID's to whom the notification will be assigned to.
                -`notification_of`: the object for which the notifictation is created for (Task/Event).          
        '''
        
        '''At the first step, the function will create a new Object of Notifications'''
        
        # get the object of notification_type, the passed value of the notification type must be the pk of the object
        notification_type = NotificationTypes.objects.get(pk=notification_type)
        timestamp=datetime.now()
        print("date time created")
        try:
            # get the object of members, the passed value of created by must be an instance of Members
            created_by=Members.objects.get(ieee_id=created_by)
            
            # create new object of Notifications
            new_notification = Notifications.objects.create(
                type=notification_type,timestamp=timestamp,title=title,general_message=general_message,
                inside_link=inside_link,created_by=created_by,notification_of=notification_of
            )
            print("here1")
            # save the new instance of notification
            new_notification.save()
                        
        except Exception as e:
            # if the members instance is not found, create it under admin privilege
            
            # create new object of Notifications without created_by option
            new_notification = Notifications.objects.create(
                type=notification_type,timestamp=timestamp,title=title,general_message=general_message,
                inside_link=inside_link,notification_of=notification_of,event = event
            )
            print("here2")
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
                tokens = PushNotification.objects.filter(member=reciever)
                #sending to all the tokens
                for token in tokens:
                    push_notification.send_push_notification(title,general_message,token.fcm_token,inside_link)
            return True
        
        except Exception as e:
            NotificationHandler.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
            

    def update_notification(notification_of, notification_type, contents=None):

        '''This function updates old notification instances, marks them as unread for all related users and changes the timestamp to current to show the notification higher in list
                -`notification_of`: it is the instance of the object whose notification is to be updated
                -`notification_type`: must be a pk of an NotificationTypes object
                -`contents`: a dict in which the keys must be of a field of Notifications that needs to update and the respective values to update with
        '''

        try:
            notification=Notifications.objects.get(object_id=notification_of.pk, type=notification_type)
            timestamp = datetime.now()
            
            #if there is contents then update each content
            if contents:
                for field, value in contents.items():
                    try:
                        # Check if the field exists in the model
                        Notifications._meta.get_field(field)
                        # Set the value to the field
                        setattr(notification, field, value)
                    except:
                        print(f"Field '{field}' does not exist in {Notifications.__name__}")
            
            #update timestamp to show it at the top of the user's notifications list
            notification.timestamp = timestamp
            notification.save()

            member_notifications = MemberNotifications.objects.filter(notification=notification)

            #Set all the member notifications to unread
            for member in member_notifications:
                member.is_read = False
                member.save()
                tokens = PushNotification.objects.filter(member=member.member)
                #sending to all the tokens
                for token in tokens:
                    push_notification.send_push_notification(member.notification.title,member.notification.general_message,token.fcm_token)
            
            return True
        except:
            return False

    def has_notification(notification_of, notification_type):

        '''This functions check if a notification exists or not. Returns a boolean
                -`notification_of`: Stores the object for which we are searching
                -`notification_type`: Type of the notification we are searching
        
        '''

        notification_exists=Notifications.objects.filter(object_id=notification_of.pk, type=notification_type).exists()
        if type(notification_of) == Task:
            return False
        return notification_exists

    def mark_as_read(member_notification_id):

        '''This functions marks a notification as read
                -`member_notification_id`: The id of the member_notification object        
        '''
        
        member_notification = MemberNotifications.objects.get(id = member_notification_id)
        member_notification.is_read = True
        member_notification.save()

    def mark_as_unread(member_notification_id):

        '''This functions marks a notification as unread
                -`member_notification_id`: The id of the member_notification object        
        '''
        timestamp=datetime.now()
        member_notification = MemberNotifications.objects.get(id = member_notification_id)
        member_notification.is_read = False
        member_notification.notification.timestamp = timestamp
        member_notification.save()

    def delete_member_notification(request,member_notification_id):
        
        '''This function will remove the notification that the user requested to be deleted'''
        
        member_notification = MemberNotifications.objects.get(id = member_notification_id)
        object_type = member_notification.notification.content_type
        try:
            if object_type.name == "Task":
                object_id = member_notification.notification.object_id
                task = Task.objects.get(pk = object_id)
                if task.is_task_completed and member_notification.member in task.members.all():
                    member_notification.delete()
                    return True
                #if member not in the or is removed task, allowing to delete
                elif member_notification.member not in task.members.all():
                    member_notification.delete()
                    return True
                else:
                    return False
            else:
                member_notification.delete()
                return True
        except:
            member_notification.delete()
            return True
    
    def notification_to_a_member(request,notification_of,title,message,inside_link,notification_type,member):

        '''This function will send the notification to the specified member only'''

        general_message=message
        if NotificationHandler.has_notification(notification_of, notification_type):
            print("exist notification")
            NotificationHandler.update_notification(notification_of, notification_type, {'general_message':general_message})
        else:
            try:
                notification_created_by=Members.objects.get(ieee_id=request.user.username)
            except:
                notification_created_by=None

            # this shows an admin if the task was created by an admin, otherwise shows the member name
            receiver_list = []
            print("receiver list created")
            receiver_list.append(member.ieee_id)
            notification_created_by_name = "An admin" if notification_created_by is None else notification_created_by.name
            print("notification created by name now going to creating")
            NotificationHandler.create_notifications(notification_type=notification_type.pk,
                                                    title=title,
                                                    general_message=general_message,
                                                    inside_link=inside_link,
                                                    created_by=notification_created_by_name,
                                                    reciever_list=receiver_list,
                                                    notification_of=notification_of)
            
    def delete_notification(notification_type, notification_of):
        
        try:
            notification=Notifications.objects.get(object_id=notification_of.pk, type=notification_type)
            notification.delete()
            return True
        except:
            return False

    def send_custom_notification(request,notification_title,notification_link,notification_description,selected_member_ids):

        '''This function sends the custom notifications'''
        try:
            created_by = Members.objects.get(ieee_id = request.user.username)
            notification = Notifications.objects.create(type = NotificationHandler.custom_notification_type,
                                                    notification_of = None,timestamp = datetime.now(),title = notification_title,
                                                    general_message = notification_description,inside_link = notification_link,
                                                    created_by = created_by)
        except:
            notification = Notifications.objects.create(type = NotificationHandler.custom_notification_type,
                                                    notification_of = None,timestamp = datetime.now(),title = notification_title,
                                                    general_message = notification_description,inside_link = notification_link)
        
        notification.save()
        for member_id in selected_member_ids:
            member = Members.objects.get(ieee_id = member_id)
            member_notification = MemberNotifications.objects.create(notification = notification,member = member,is_read = False)
            member_notification.save()
            tokens = PushNotification.objects.filter(member=member)
            for token in tokens:
                push_notification.send_push_notification(member_notification.notification.title,member_notification.notification.general_message,token.fcm_token,notification_link)

        return True
        
    def notification_history():

        '''This function will return the details custom notification sent'''
        
        custom_notification_history=Notifications.objects.filter(type = NotificationHandler.custom_notification_type).order_by('-timestamp')
        notification_dict = {}
        for notification in custom_notification_history:
            mem_list = []
            members = MemberNotifications.objects.filter(notification = notification)
            for m in members:
                mem_list.append(m.member)
            notification_dict[notification] = mem_list
        
        return notification_dict
