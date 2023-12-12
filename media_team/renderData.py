from users.models import Members
from port.models import Teams,Roles_and_Position
from system_administration.models import Media_Data_Access
from .models import Media_Images,Media_Link
from django.conf import settings
from central_events.models import Events
import os
import logging
from datetime import datetime
from system_administration.system_error_handling import ErrorHandling
import traceback
class MediaTeam:
    logger=logging.getLogger(__name__)

    def get_member_with_postion(position):
        '''Returns Media Team Members with positions'''
        team_members=Members.objects.filter(team=MediaTeam.get_team_id(),position=position)
        return team_members

    def get_team_id():
        
        '''Gets the team id from the database only for Media Team. Not the right approach'''
        
        team=Teams.objects.get(team_name="Media")
        return team
    
    def load_manage_team_access():
        return Media_Data_Access.objects.all()
    
    def load_team_members():
        
        '''This function loads all the team members for the Media team'''

        load_team_members=Members.objects.filter(team=MediaTeam.get_team_id()).order_by('position')
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    
    def add_member_to_team(ieee_id,position):
        team_id=MediaTeam.get_team_id().id
        Members.objects.filter(ieee_id=ieee_id).update(team=Teams.objects.get(id=team_id),position=Roles_and_Position.objects.get(id=position))

    def media_manage_team_access_modifications(manage_team_access,ieee_id):
        try:
            Media_Data_Access.objects.filter(ieee_id=ieee_id).update(manage_team_access=manage_team_access)
            return True
        except Media_Data_Access.DoesNotExist:
            return False
        
    def remove_member_from_manage_team_access(ieee_id):
        try:
            Media_Data_Access.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
        
    def add_member_to_manage_team_access(ieee_id):
        try:
            if(Media_Data_Access.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=Media_Data_Access(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False
        
    def media_manage_team_access(ieee_id):
        try:
            user = Media_Data_Access.objects.get(ieee_id = ieee_id)
            if(user.manage_team_access):
                return True
            else:
                return False
        except:
            return False
        
    def add_links_and_images(picture_drive_link,logo_picture_drive_link,selected_images,event_id):
        
        '''This functions adds the links and images to the database for graphics team'''
        try:
            #Updating the media links and logo links. If does not exist then new ones are created
            try:
                media_link = Media_Link.objects.get(event_id = Events.objects.get(pk=event_id))
                media_link.media_link = picture_drive_link
                media_link.logo_link = logo_picture_drive_link

            except Media_Link.DoesNotExist:
                media_link = Media_Link.objects.create(event_id = Events.objects.get(pk=event_id),media_link = picture_drive_link,logo_link = logo_picture_drive_link)
    
            media_link.save()
            
            if len(selected_images)>0:
                
                #If images are uploaded then initailly checking if for this event any picture were intially uploaded or not
                #If not then new image is being added to the database for the event

                uploaded_images = Media_Images.objects.filter(event_id=Events.objects.get(pk=event_id))
                number_of_uploaded_images = len(uploaded_images)
                if number_of_uploaded_images>=6:
                    return False
                    
                else:     
                    for image in selected_images:
                        Image_save = Media_Images.objects.create(event_id = Events.objects.get(pk=event_id),selected_images = image)
                        Image_save.save()
            return True
        except Exception as e:
            MediaTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    def remove_image(image_url,event_id):
        try:

            #Deleting the image that the user wants from the database and from the OS

            image = Media_Images.objects.get(event_id = Events.objects.get(pk = event_id),selected_images = image_url)
            path = settings.MEDIA_ROOT+str(image.selected_images)
            os.remove(path)
            image.delete()
            return True
        except Exception as e:
            MediaTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False



            


            



        
            
