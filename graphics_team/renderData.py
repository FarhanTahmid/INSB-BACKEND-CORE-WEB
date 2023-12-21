from central_branch.renderData import Branch
from users.models import Members
from port.models import Teams,Roles_and_Position
from system_administration.models import Graphics_Data_Access
import os
import logging
from datetime import datetime
from system_administration.system_error_handling import ErrorHandling
import traceback
from .models import Graphics_Link,Graphics_Banner_Image,Graphics_Form_Link
from central_events.models import Events
from django.conf import settings
class GraphicsTeam:

    logger=logging.getLogger(__name__)

    def get_co_ordinator():
        roles = Roles_and_Position.objects.get(is_co_ordinator=True)
        members = Members.objects.filter(position=roles,team=GraphicsTeam.get_team_id())
        print(members)
        return members

    def get_officer():
        roles = Roles_and_Position.objects.get(is_officer = True,is_co_ordinator=False)
        members = Members.objects.filter(position = roles,team=GraphicsTeam.get_team_id())
        
        print(roles,members)
        return members


    def get_member_with_postion(position):
        '''Returns Graphics Team Members with positions'''
        team_members=Members.objects.filter(team=GraphicsTeam.get_team_id(),position=position)
        return team_members

    def get_team():
        
        '''Gets the team from the database only for Graphics Team. Not the right approach'''
        
        team=Teams.objects.get(primary=10)
        return team
    
    def load_data_access():
        return Graphics_Data_Access.objects.all()
    
    def load_team_members():
        
        '''This function loads all the team members for the Graphics team'''

        # load_team_members=Members.objects.filter(team=GraphicsTeam.get_team_id()).order_by('position')
        load_team_members=Branch.load_team_members(team_primary=GraphicsTeam.get_team().primary)
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
        
    def get_team_id():
        
        '''Gets the team id from the database only for Media Team. Not the right approach'''
        
        team=Teams.objects.get(team_name="Graphics")
        return team

    def add_member_to_team(ieee_id,position):
        team_id=GraphicsTeam.get_team_id().id
        Members.objects.filter(ieee_id=ieee_id).update(team=Teams.objects.get(id=team_id),position=Roles_and_Position.objects.get(id=position))

    def graphics_manage_team_access_modifications(manage_team_access, event_access, ieee_id):
        try:
            Graphics_Data_Access.objects.filter(ieee_id=ieee_id).update(manage_team_access=manage_team_access, event_access=event_access)
            return True
        except Graphics_Data_Access.DoesNotExist:
            return False
        
    def remove_member_from_manage_team_access(ieee_id):
        try:
            Graphics_Data_Access.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
        
    def add_member_to_manage_team_access(ieee_id):
        try:
            if(Graphics_Data_Access.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=Graphics_Data_Access(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False
        
    def graphics_manage_team_access(ieee_id):
        try:
            user = Graphics_Data_Access.objects.get(ieee_id = ieee_id)
            if(user.manage_team_access):
                return True
            else:
                return False
        except:
            return False
        
    def add_links_and_images(graphics_drive_link,selected_image,event_id):

        '''This functions adds the links and images to the database for graphics team'''

        try:
            #Updating the media link. If does not exist then new ones are created
            try:
                graphics_link = Graphics_Link.objects.get(event_id = Events.objects.get(pk=event_id))
                graphics_link.graphics_link = graphics_drive_link
            except Graphics_Link.DoesNotExist:
                graphics_link = Graphics_Link.objects.create(event_id = Events.objects.get(pk=event_id),graphics_link = graphics_drive_link)

            graphics_link.save()

            if selected_image != None:
                upload_image = Graphics_Banner_Image.objects.create(event_id=Events.objects.get(pk=event_id),selected_image = selected_image)
                upload_image.save()
            return True
        except Exception as e:
            GraphicsTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def remove_image(image_url,event_id):
        try:

            #Deleting the image that the user wants from the database and from the OS

            image = Graphics_Banner_Image.objects.get(event_id = Events.objects.get(pk = event_id),selected_image = image_url)
            path = settings.MEDIA_ROOT+str(image.selected_image)
            os.remove(path)
            image.delete()
            return True
        except Exception as e:
            GraphicsTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def add_graphics_form_link(event_id,form_link,title):

        '''This function adds the graphics form links to the respective event'''

        try:
            event = Graphics_Form_Link.objects.create(event_id = Events.objects.get(pk = event_id),graphics_form_link_name = title,graphics_form_link = form_link)
            event.save()
            return True
        except Exception as e:
            GraphicsTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def get_all_graphics_form_link(event_id):

        return Graphics_Form_Link.objects.filter(event_id = Events.objects.get(pk = event_id))
    
    def update_graphics_form_link(form_link,title,pk):

        '''This function updates the graphics form links to the respective event'''
        try:
            event = Graphics_Form_Link.objects.get(pk = pk)
            event.graphics_form_link_name = title
            event.graphics_form_link = form_link
            event.save()
            return True
        except Exception as e:
            GraphicsTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    def remove_graphics_form_link(id):
        try:

            Graphics_Form_Link.objects.get(pk = id).delete()
            return True
        except Exception as e:
            GraphicsTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False