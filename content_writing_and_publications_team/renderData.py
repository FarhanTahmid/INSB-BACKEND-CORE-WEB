from central_branch.renderData import Branch
from django.shortcuts import get_object_or_404
from users.models import Members
from port.models import Teams,Roles_and_Position
from system_administration.models import CWP_Data_Access
from .models import Content_Notes, Content_Team_Document, Content_Team_Documents_Link
import logging
import traceback
from system_administration.system_error_handling import ErrorHandling
from datetime import datetime
from central_events.models import Events
from .forms import Content_Form
class ContentWritingTeam:

    logger=logging.getLogger(__name__)

    def get_team():
        team = Teams.objects.get(primary=2)
        return team

    def get_team_id():
        
        '''Gets the team id from the database only for content writing and publications Team. Not the right approach'''
        
        team=Teams.objects.get(team_name="Content Writing and Publications")
        return team.id
    def load_manage_team_access():
        return CWP_Data_Access.objects.all()
    
    def load_team_members():
        
        '''This function loads all the team members for the content wrtiting and publications team'''

        load_team_members=Branch.load_team_members(team_primary=ContentWritingTeam.get_team().primary)
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    
    def add_member_to_team(ieee_id,position):
        team_id=ContentWritingTeam.get_team_id()
        Members.objects.filter(ieee_id=ieee_id).update(team=Teams.objects.get(id=team_id),position=Roles_and_Position.objects.get(id=position))

    def cwp_manage_team_access_modifications(manage_team_access, event_access, ieee_id):
        try:
            CWP_Data_Access.objects.filter(ieee_id=ieee_id).update(manage_team_access=manage_team_access, event_access=event_access)
            return True
        except CWP_Data_Access.DoesNotExist:
            return False
        
    def remove_member_from_manage_team_access(ieee_id):
        try:
            CWP_Data_Access.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
        
    def add_member_to_manage_team_access(ieee_id):
        try:
            if(CWP_Data_Access.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=CWP_Data_Access(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False

    def cwp_manage_team_access(ieee_id):
        try:
            user = CWP_Data_Access.objects.get(ieee_id = ieee_id)
            if(user.manage_team_access):
                return True
            else:
                return False
        except:
            return False
        
    def creating_note(title,note,event_id):

        '''This function creates notes for the specific event. It takes the note title, note description and event id'''

        try:
            new_note = Content_Notes.objects.create(event_id = Events.objects.get(pk = event_id),title = title,captions = note)
            new_note.save()
            return True
        except Exception as e:
            ContentWritingTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def load_note_content(event_id):
        ''' This function is used to load all the notes added by CWP Team for a specific event. It takes event id as parameter and returns a dictionary with note and its associated form object '''
    
        all_notes_for_particular_event = Content_Notes.objects.filter(event_id = Events.objects.get(pk=event_id))
        notes_and_content = {}
        for note in all_notes_for_particular_event:
            form = Content_Form(instance=note)
            notes_and_content.update({note:form})
        return notes_and_content

    def remove_note(note_id):
        ''' This function is used to delete a note. It takes a note id '''
        try:
            note = Content_Notes.objects.get(id=note_id)
            note.delete()
            return True
        except Exception as e:
            ContentWritingTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def update_note(note_id, title, note_content):
        ''' This function is used to update a note of CWP Team. It takes note id, note title and note content as parameters. '''
        try:
            note = Content_Notes.objects.get(id=note_id)
            note.title = title
            note.notes = note_content
            note.save()
            return True
        except Exception as e:
            ContentWritingTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def update_event_details(event_id, event_description, drive_link):
        ''' This function is used for CWP Team to update event details [Event Descrition & Drive link]. It takes event id, event description and drive link as parameters '''
        try:
            event = Events.objects.get(id=event_id)
            event.event_description = event_description
            event.save()

            #If drive link is given
            if(drive_link != ''):
                #If a drive link existed previously then update it
                if(Content_Team_Documents_Link.objects.filter(event_id=event_id).exists()):
                    Content_Team_Documents_Link.objects.update(event_id=event_id, documents_link=drive_link)
                else:
                #Else create a new link
                    documents_link = Content_Team_Documents_Link.objects.create(event_id=event, documents_link=drive_link)
                    documents_link.save()
            else:
            #Drive link is not given
                #If a drive link exists then delete it from database
                if(Content_Team_Documents_Link.objects.filter(event_id=event_id).exists()):
                    Content_Team_Documents_Link.objects.get(event_id=event_id).delete()

            return True
        except Exception as e:
            ContentWritingTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def upload_files(event_id, file_list):
        ''' This function is used to upload files (single or multiple) for CWP Team. It takes event id and file list as parameters '''
        try:
            for document in file_list:
                doc = Content_Team_Document.objects.create(event_id=Events.objects.get(id=event_id), document=document)
                doc.save()
                
            return True
            
        except Exception as e:
            ContentWritingTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def delete_file(file_id):
        ''' This function is used to delete a file of CWP Team. It takes a file id as parameter '''
        try:
            doc = Content_Team_Document.objects.get(id=file_id)
            doc.document.delete()
            doc.delete()
            return True
        except Exception as e:
            ContentWritingTeam.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False       
        