import os
from bs4 import BeautifulSoup
from django.http import Http404
from django.urls import reverse
from central_events.google_calendar_handler import CalendarHandler
from chapters_and_affinity_group.get_sc_ag_info import SC_AG_Info
from insb_port import settings
from main_website.models import About_IEEE, HomePageTopBanner, IEEE_Bangladesh_Section, IEEE_NSU_Student_Branch, IEEE_Region_10, Page_Link,FAQ_Question_Category,FAQ_Questions,HomePage_Thoughts,IEEE_Bangladesh_Section_Gallery
from notification.models import NotificationTypes
from notification.notifications import NotificationHandler
from port.models import Teams,Roles_and_Position,Chapters_Society_and_Affinity_Groups,Panels
from port.renderData import PortData
from users.models import Members,Panel_Members,Alumni_Members
from django.db import DatabaseError
from system_administration.models import MDT_Data_Access
from central_events.models import Event_Feedback, Google_Calendar_Attachments, SuperEvents,Events,InterBranchCollaborations,IntraBranchCollaborations,Event_Venue,Event_Permission,Event_Category
from events_and_management_team.models import Venue_List, Permission_criteria
from system_administration.render_access import Access_Render
from system_administration.system_error_handling import ErrorHandling
# from users.models import Executive_commitee,Executive_commitee_members
from membership_development_team.renderData import MDT_DATA
from datetime import datetime
import sqlite3
from django.contrib import messages
from system_administration.models import Branch_Data_Access
from django.db.utils import IntegrityError
import traceback
import logging
from system_administration.system_error_handling import ErrorHandling
from graphics_team.models import Graphics_Banner_Image
from media_team.models import Media_Images
from content_writing_and_publications_team.models import Content_Team_Document
from recruitment.models import recruited_members

class Branch:

    logger=logging.getLogger(__name__)
    try:
        event_notification_type = NotificationTypes.objects.get(type="Event")
    except:
        event_notification_type = None

    
    def getBranchID():
        '''This Method returns the object of Branch from Society chapters and AG Table'''
        try:
            return Chapters_Society_and_Affinity_Groups.objects.get(primary=1)
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Can not return Branch ID. Something went wrong!")
            return False
    
    def get_selected_venues(event_id):
        lis = []
        venues = Event_Venue.objects.filter(event_id = event_id)
        for i in venues:
            lis.append(i.venue_id.venue_name)
        return lis

    def reset_all_teams():
        '''To remove all members in all teams and assigning them as general memeber'''
        try:
            all_memebers_in_team = Members.objects.all()
            all_memebers_in_team.update(team=None,position = Roles_and_Position.objects.get(id=13))
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Can not reset all team. Something went wrong!")
            return False  
    
    def new_recruitment_session(team_name):

        '''Method to create a new recruitment session for team, by creating new Team'''
        try:
            new_team = Teams(team_name = team_name)
            new_team.save()
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Can not create new recruitment sesssion. Something went wrong!")
            return False
    
    def add_event_venue(venue_name):

        '''This function adds new venue to the database'''
        try:
            venue = Venue_List.objects.create(venue_name = venue_name)
            venue.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Can not create new event venue. Something went wrong!")
            return False

    
    def add_event_type_for_group(event_type,group_number):
        
        '''This function adds new event category according to the group''' 

        try:
            #lower letter casing
            event_type_lower = event_type.lower()
            event_type_lower_with_no_space = event_type_lower.replace(" ","") 
            #creating a new list
            catagories = []
            #getting all catagories of particular society
            registered_event_categories = Event_Category.objects.filter(event_category_for=Chapters_Society_and_Affinity_Groups.objects.get(primary = group_number))
            #making all the catagories to lower casing
            for catagory in registered_event_categories:
                word = catagory.event_category.lower()
                word = word.replace(" ","")
                catagories.append(word)
            #if same exists then preventing addition
            if event_type_lower_with_no_space in catagories:
                return False 
            else:
                new_event_type = Event_Category.objects.create(event_category=event_type,event_category_for = Chapters_Society_and_Affinity_Groups.objects.get(primary = group_number))
                new_event_type.save()
                return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Can not create new event type. Something went wrong!")
            return False
        

    def load_teams():
        
        '''This function returns all the teams in the database'''
        try:
            teams=Teams.objects.filter(team_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=1)).values('primary','team_name') #returns a list of dictionaryies with the id and team name
            return teams
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def load_team_members(team_primary):
        '''This function loads all the team members from the database and also checks if the member is included in the current panel'''
        team=Teams.objects.get(primary=team_primary)
        team_id=team.id
        get_users=Members.objects.order_by('-position').filter(team=team_id)
        get_current_panel=Branch.load_current_panel()
        team_members=[]
        if(get_current_panel is not None):
            for i in get_users:
                if(Panel_Members.objects.filter(member=i.ieee_id,tenure=get_current_panel.pk).exists()):
                    team_members.append(i)

        return team_members
    
    def register_mega_events(event_organiser,super_event_name,super_event_description,start_date,end_date,banner_image):
        
        '''This function registers the mega event'''

        try:
            if start_date=='' and end_date=='':
                saving_data = SuperEvents(mega_event_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=event_organiser),super_event_name=super_event_name,super_event_description=super_event_description,banner_image=banner_image)
                saving_data.save()
                return True
            elif end_date=='':
                saving_data = SuperEvents(mega_event_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=event_organiser),super_event_name=super_event_name,super_event_description=super_event_description,start_date=start_date,banner_image=banner_image)
                saving_data.save()
                return True
            elif start_date=='':
                saving_data = SuperEvents(mega_event_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=event_organiser),super_event_name=super_event_name,super_event_description=super_event_description,end_date=end_date,banner_image=banner_image)
                saving_data.save()
                return True
            else:
                saving_data = SuperEvents(mega_event_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=event_organiser),super_event_name=super_event_name,super_event_description=super_event_description,start_date=start_date,end_date=end_date,banner_image=banner_image)
                saving_data.save()
                return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def update_mega_event(mega_event_id,super_event_name,super_event_description,start_date,end_date,publish_mega_event,banner_image):
        try:
            mega_event = SuperEvents.objects.get(id=mega_event_id)
            mega_event.super_event_name = super_event_name
            mega_event.super_event_description = super_event_description
            if publish_mega_event == 'on':
                mega_event.publish_mega_event = True
            else:
                mega_event.publish_mega_event = False
            if start_date:
                mega_event.start_date = start_date
            else:
                mega_event.start_date = None
            if end_date:
                mega_event.end_date = end_date
            else:
                mega_event.end_date = None

            if banner_image is not None:
                file = mega_event.banner_image
                if not file:
                    mega_event.banner_image = banner_image
                else:
                    path = settings.MEDIA_ROOT+str(file)
                    if os.path.exists(path):
                        os.remove(path)
                    mega_event.banner_image = banner_image
            mega_event.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def delete_mega_event_banner(mega_event_id):
        try:
            mega_event = SuperEvents.objects.get(id=mega_event_id)
            path = settings.MEDIA_ROOT+str(mega_event.banner_image)
            if os.path.exists(path):
                os.remove(path)
            mega_event.banner_image = None
            mega_event.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def delete_mega_event(mega_event_id):
        try:
            mega_event = SuperEvents.objects.get(id=mega_event_id)
            events = Events.objects.filter(super_event_id=mega_event)
            for event in events:
                event.super_event_id = None
                event.save()
            mega_event_banner_image_path = settings.MEDIA_ROOT + str(mega_event.banner_image)
            if os.path.isfile(mega_event_banner_image_path):
                os.remove(mega_event_banner_image_path)
            mega_event.delete()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    
    def register_event_page1(super_event_id,event_name,event_type_list,event_description,event_start_date,event_end_date,event_organiser=None):
            '''This method creates an event and registers data which are provided in event page1. Returns the id of the event if the method can create a new event successfully
            TAKES SUPER EVENT NAME, EVENT NAME, EVENT DESCRIPTION AS STRING. TAKES PROBABLE & FINAL DATE ALSO AS INPUT'''
            if event_organiser==None:
                event_organiser = 1

            if(super_event_id=="null"):
                    
                    #now create the event as super event is null
                    if(event_end_date==''):
                        
                        try:
                            #create event without final date included
                            new_event=Events.objects.create(
                            event_name=event_name,
                            event_description=event_description,
                            start_date = event_start_date,
                            event_organiser = Chapters_Society_and_Affinity_Groups.objects.get(primary = str(event_organiser))
                            )
                            new_event.save()
                            new_event.event_type.add(*event_type_list)
                            new_event.save()
                            return new_event.id
                        except:
                            new_event.delete()
                            return False #general error
                    else:
                        try:
                            #create event with final date included
                            new_event=Events(
                            event_name=event_name,
                            event_description=event_description,
                            start_date = event_start_date,
                            end_date = event_end_date,
                            event_organiser = Chapters_Society_and_Affinity_Groups.objects.get(primary = str(event_organiser))
                            )
                            new_event.save()
                            new_event.event_type.add(*event_type_list)
                            new_event.save()
                            return new_event.id
                        except:
                            new_event.delete()
                            return False #general error    
            else:
                    #now create the event under super event in the event models
                    
                    if(event_end_date==''):
                        
                        try:
                            get_super_event_id = SuperEvents.objects.get(id = super_event_id)
                            print(get_super_event_id.super_event_name)
                            new_event=Events.objects.create(
                            super_event_id=get_super_event_id,
                            event_name=event_name,
                            event_description=event_description,
                            start_date = event_start_date,
                            event_organiser = Chapters_Society_and_Affinity_Groups.objects.get(primary = str(event_organiser))
                            )
                            new_event.save()
                            new_event.event_type.add(*event_type_list)
                            new_event.save()
                            return new_event.id
                        except:
                            new_event.delete()
                            return False #general Error
                    else:
                        try:
                            get_super_event_id = SuperEvents.objects.get(id = super_event_id)
                            new_event=Events(
                            super_event_id=get_super_event_id,
                            event_name=event_name,
                            event_description=event_description,
                            start_date = event_start_date,
                            end_date = event_end_date,
                            event_organiser = Chapters_Society_and_Affinity_Groups.objects.get(primary = str(event_organiser))
                            )
                            new_event.save()
                            new_event.event_type.add(*event_type_list)
                            new_event.save()
                            return new_event.id
                        except:
                            new_event.delete()
                            return False
        
    def register_event_page2(inter_branch_collaboration_list,intra_branch_collaboration,event_id):
        
            '''This method creates collaborations related to the events and registers data which are provided in event page2
            TAKES INTER BRANCH COLLABORATION LIST, INTRA BRANCH COLLABORATION STRING AND EVENT ID AS PARAMETER'''

        #checking who organised the event
            event_organiser = Events.objects.get(pk = event_id).event_organiser.primary
            group_primary = Chapters_Society_and_Affinity_Groups.objects.get(primary = str(event_organiser)).primary
            if group_primary != 1:
                if inter_branch_collaboration_list[0]=="null":
                    inter_branch_collaboration_list[0]='1'
                else:
                    if '1' not in inter_branch_collaboration_list:
                        inter_branch_collaboration_list.append('1')
                        print(inter_branch_collaboration_list)
            print(inter_branch_collaboration_list)
        #first check if both the collaboration options are null. If so, do register nothing on database and redirect to the next page
            if(inter_branch_collaboration_list[0]=="null" and intra_branch_collaboration==""):
                return True #not registering any collaboration, go to the third page
            #check if any intra branch collab is entered while inter branch collab option is still set to null. If so, then only register for intra branch collaboration option
            elif(inter_branch_collaboration_list[0]=="null" and intra_branch_collaboration!=""):
                # Do the intra branch collab only
                
               
                #check if an event exists with the same id. if so just update the collaboration_with field
                check_for_existing_events=IntraBranchCollaborations.objects.filter(event_id=event_id)
                if(check_for_existing_events.exists()):
                    check_for_existing_events.update(collaboration_with=intra_branch_collaboration)
                    return True #intra branch collab updated, now go to third page
                else:
                    #if the event does not exist in the intra branch collaboration table, just register for a new collaboration in the database
                    new_event_intra_branch_collaboration=IntraBranchCollaborations(
                        event_id=Events.objects.get(id=event_id),
                        collaboration_with=intra_branch_collaboration
                    )
                    print("here")
                    new_event_intra_branch_collaboration.save()
                    return True #intra branch collab created, now go to third page
                
                
            #now checking for the criterias where there are inter branch collaboration
            else:
                #checking if the intra branch collab option is still null. If null, only register for intra branch collaboration
                if(intra_branch_collaboration==None):
                    for id in inter_branch_collaboration_list:
                        
                            #check for existing events with the same inter branch collab
                            # check_for_existing_events=InterBranchCollaborations.objects.filter(event_id=event_id,collaboration_with=id)
                            # if(check_for_existing_events.exists()):
                            #     check_for_existing_events.update(collaboration_with=id) #this piece of code is really not needed just used to avoid errors and usage of extra memory
                            # else:
                                #if there is no previous record of this event with particular collab option, register a new one
                                    new_event_inter_branch_collaboration=InterBranchCollaborations(
                                        event_id=Events.objects.get(id=event_id),
                                        collaboration_with=Chapters_Society_and_Affinity_Groups.objects.get(primary = id)
                                    )   
                                    new_event_inter_branch_collaboration.save()
                                    return True
                        
                #now register for the both collaboration option when both are filled
                else:
                    #firstly for inter branch collaboration option, register for events as usual
                    for id in inter_branch_collaboration_list:
                        
                            #check for existing events with the same inter branch collab
                            # check_for_existing_events=InterBranchCollaborations.objects.filter(event_id=event_id,collaboration_with=id)
                            # if(check_for_existing_events.exists()):
                            #     check_for_existing_events.update(collaboration_with=id) #this piece of code is really not needed just used to avoid errors and usage of extra memory
                            # else:
                            #if there is no previous record of this event with particular collab option, register a new one
                                new_event_inter_branch_collaboration=InterBranchCollaborations(
                                    event_id=Events.objects.get(id=event_id),
                                    collaboration_with=Chapters_Society_and_Affinity_Groups.objects.get(primary = id) 
                                ) 
                                new_event_inter_branch_collaboration.save()
                                
                            
                    #secondly for intra branch collaboration options
                    
                    
                    #check if an event exists with the same id. if so just update the collaboration_with field
                    check_for_existing_events=IntraBranchCollaborations.objects.filter(event_id=event_id)
                    if(check_for_existing_events.exists()):
                        check_for_existing_events.update(collaboration_with=intra_branch_collaboration)
                        print('intra branch collab updated, now go to third page')
                    else:
                        #if the event does not exist in the intra branch collaboration table, just register for a new collaboration in the database
                        new_event_intra_branch_collaboration=IntraBranchCollaborations(
                            event_id=Events.objects.get(id=event_id),
                            collaboration_with=intra_branch_collaboration
                        )
                        new_event_intra_branch_collaboration.save()
                        return True # intra branch collab created, now go to third page


    def register_event_page3(venue_list,permission_criteria_list,event_id):
        '''This method creates venues and permissions related to the events and registers data which are provided in event page3
        TAKES LISTS OF VENUES AND PERMISSIONS AS PARAMETER. Also takes event id to register with respect to it'''
        
        #to update venues first check if the length is greater than 0. It confirms atleast one venue was selected
        if(len(venue_list)>0):
            #if the condition is correct now extract the values from the list, and register with the corresponding event id and venue id to the models.
            #this data is stored in the Event_Venue Models inside insb_centrals models.py
            for venue in venue_list:
                try:
                    #check for already existing record with same event_id and venue
                    check_for_existing_venue=Event_Venue.objects.filter(event_id=event_id,venue_id=venue)
                    if(check_for_existing_venue.exists()):
                        print("Exists")
                        check_for_existing_venue.update(venue_id=venue) #this piece of code is really not needed just used to avoid errors and usage of extra memory
                    else:
                        print("Doesn't")
                        #now register the venue with the corresponding event_id
                        register_venue=Event_Venue(
                            event_id=Events.objects.get(id=event_id),
                            venue_id=Venue_List.objects.get(id=venue)
                            )
                        register_venue.save()
                except:
                    return False #return False if anything goes wrong with the database setting process
        else:
            pass
        
        
        for permission in permission_criteria_list:
                #checking if null was selected for the process
                if(permission!="null"):
                    try:
                        #check if same record exists
                        check_for_existing_permission=Event_Permission.objects.filter(event_id=event_id,permission_id=permission)
                        if(check_for_existing_permission.exists()):
                            check_for_existing_permission.update(permission_id=permission) #this piece of code is really not needed just used to avoid errors and usage of extra memory
                
                        else:
                            register_permission_criteria=Event_Permission(
                                event_id=Events.objects.get(id=event_id),
                                permission_id=Permission_criteria.objects.get(id=permission)
                            )
                            register_permission_criteria.save()
                    except:
                        return False
                else:
                    pass

    def update_event_details(request, event_id, event_name, event_description, super_event_id, event_type_list,publish_event, event_start_date, event_end_date, inter_branch_collaboration_list, intra_branch_collaboration, venue_list_for_event,
                             flagship_event,registration_fee,registration_fee_amount,more_info_link,form_link,is_featured_event):
            ''' Update event details and save to database '''

        
            #Get the selected event details from database
            event = Events.objects.get(pk=event_id)

            create_notification = False
            delete_notification = False
            update_notification = False
            dt = datetime.strptime(event_start_date, '%Y-%m-%dT%H:%M')
            if(publish_event and not event.publish_in_main_web):
                create_notification = True
            elif(not publish_event and event.publish_in_main_web):
                delete_notification = True
            elif((event_name != event.event_name or str(dt) != str(event.start_date.astimezone(dt.tzinfo))[:-6]) and event.publish_in_main_web):
                update_notification = True

            if event_end_date == "":
                event_end_date = None
            #Check if super id is null
            if(super_event_id == 'null'):

                #Check if date is empty
                if(event_end_date == ""):
                    #Update without date and super id
                    event.event_name = event_name
                    event.event_description = event_description
                else:
                    #Update without super id
                    event.event_name = event_name
                    event.event_description = event_description
                    event.end_date = event_end_date
            else:
                ''' Super ID is not null '''

                #Check if date is empty
                if(event_end_date == ""):
                    #Update without date
                    event.event_name = event_name
                    event.event_description = event_description
                    event.super_event_id = SuperEvents.objects.get(id=super_event_id)
                else:
                    #Update all
                    event.event_name = event_name
                    event.event_description = event_description
                    event.super_event_id = SuperEvents.objects.get(id=super_event_id)
                    event.end_date = event_end_date
                    
            #Clear event type
            event.event_type.clear()
            #Add the event types from event_type_list
            event.event_type.add(*event_type_list)
            event.start_date = event_start_date
            event.end_date = event_end_date
            ####################################################
            ######event publish/not publish trigger here####################
            ####################################################
            event.publish_in_main_web = publish_event
            event.flagship_event = flagship_event
            event.registration_fee = registration_fee
            event.registration_fee_amount = registration_fee_amount
            event.more_info_link = more_info_link
            event.form_link = form_link
            event.is_featured = is_featured_event
            event.save()
            event_venue = Event_Venue.objects.filter(event_id = event_id)

            #Clear previous event venues
            for venues in event_venue:
                venues.delete()

            #If not null then add the new venues
            if len(venue_list_for_event) > 0:
                if venue_list_for_event[0] != 'null':
                    for i in venue_list_for_event:
                        register_venue=Event_Venue(
                                    event_id=Events.objects.get(id=event_id),
                                    venue_id=Venue_List.objects.get(id=i)
                                    )
                        register_venue.save()

            if(inter_branch_collaboration_list[0] == 'null'):
                interbranchcollaborations = InterBranchCollaborations.objects.filter(event_id=event_id)
                if(interbranchcollaborations.count() != 0):
                    for i in interbranchcollaborations:
                        print(type(i.collaboration_with.primary))
                        if(i.collaboration_with.primary != 1):
                            i.delete()
            else:
                interbranchcollaborations = InterBranchCollaborations.objects.filter(event_id=event_id).values_list('collaboration_with', flat=True)
                testArray = []

                group_primary = event.event_organiser.primary
                if group_primary != 1:
                    if '1' not in inter_branch_collaboration_list:
                        inter_branch_collaboration_list.append('1')
                        

                for i in interbranchcollaborations:
                    testArray.append(str(Chapters_Society_and_Affinity_Groups.objects.get(id=i).primary))

                for i in inter_branch_collaboration_list:
                    if i not in testArray:
                        new_event_inter_branch_collaboration = InterBranchCollaborations(event_id=event, collaboration_with=Chapters_Society_and_Affinity_Groups.objects.get(primary=int(i)))
                        new_event_inter_branch_collaboration.save()

                for i in testArray:
                    if i not in inter_branch_collaboration_list:
                        InterBranchCollaborations.objects.filter(event_id=event, collaboration_with=Chapters_Society_and_Affinity_Groups.objects.get(primary=int(i))).delete()                   

            intrabranchcollaborations = IntraBranchCollaborations.objects.filter(event_id=event_id)
            if(intra_branch_collaboration == ""):
                if(intrabranchcollaborations):
                    intrabranchcollaborations.delete()
            else:
                if(intrabranchcollaborations):
                    intrabranchcollaborations.update(collaboration_with=intra_branch_collaboration)
                else:
                    IntraBranchCollaborations.objects.create(event_id=event, collaboration_with=intra_branch_collaboration)
            
            event = Events.objects.get(pk=event_id)

            if(create_notification):
                inside_link=f"{request.META['HTTP_HOST']}/events/{event.pk}"
                general_message=f"{event.start_date.strftime('%A %d, %b@%I:%M%p')} | <b>{event.event_name}</b>"
                # receiver_list=Branch.load_all_active_general_members_of_branch()
                receiver_list=Branch.get_attendee_list_from_backend(event.selected_attendee_list)
                if receiver_list == None or len(receiver_list) == 0:
                    messages.warning(request, "The attendee list is empty! Could not create notifications or notify members")
                    return True
                if(NotificationHandler.create_notifications(notification_type=Branch.event_notification_type.pk,
                                                            title="New Event has been published!",
                                                            general_message=general_message,
                                                            inside_link=inside_link,
                                                            created_by="IEEE NSU SB",
                                                            reciever_list=receiver_list,
                                                            notification_of=event,
                                                            event = event)):
                    messages.success(request, "Notifications created and sent to members!")
                else:
                    messages.warning(request, "Could not create notifications or notify members!")
            elif(update_notification):
                general_message=f"{event.start_date.strftime('%A %d, %b@%I:%M%p')} | <b>{event.event_name}</b>"
                if(NotificationHandler.update_notification(notification_type=Branch.event_notification_type, notification_of=event, contents={'general_message':general_message})):
                    messages.success(request, "Notifications updated successfully!")
                else:
                    messages.warning(request, "Could not update notifications!")
            elif(delete_notification):
                if(NotificationHandler.delete_notification(notification_type=Branch.event_notification_type,notification_of=event)):
                    messages.success(request, "Notifications deleted successfully!")
                else:
                    messages.warning(request, "Could not delete notifications!")

            if(event.google_calendar_event_id):
                if(CalendarHandler.update_event_in_calendar(request, event.google_calendar_event_id, event.event_name, None, event.start_date, event.end_date)):
                    messages.success(request, "Event updated in calendar")
                else:
                    messages.warning(request, "Could not update event in calendar")

            return True
    
    def get_attendee_list_from_backend(request, attendeeOption):
        to_attendee_final_list = []
        for option in attendeeOption:
            if(option == "general_members"):
                general_members=Branch.load_all_active_members_of_branch()
                for member in general_members:
                    to_attendee_final_list.append({
                        'displayName':member.name,
                        'email':member.email_nsu,
                    })
            elif option=="all_officers":
                # get all officers email
                branch_officers=Branch.load_all_officers_of_branch()
                for officer in branch_officers:
                    to_attendee_final_list.append({
                        'displayName':officer.name,
                        'email':officer.email_nsu,
                    })
                    # to_attendee_final_list.append({
                    #     'displayName':officer.name,
                    #     'email':officer.email_ieee,
                    # })
                            
            elif option=="eb_panel":
                # get all eb panel email
                eb_panel=Branch.load_branch_eb_panel()
                for eb in eb_panel:
                    #if is faculty then skip
                    if not eb.position.is_faculty:
                        to_attendee_final_list.append({
                            'displayName':eb.name,
                            'email':eb.email_nsu,
                        })
                        # to_attendee_final_list.append({
                            # 'displayName':eb.name,
                            # 'email':eb.email_ieee,
                        # })
            elif option=="excom_branch":
                # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                eb_panel=Branch.load_branch_eb_panel()
                branch_ex_com=PortData.get_branch_ex_com_from_sc_ag(request=request)
                for eb in eb_panel:
                    #If is faculty then skip
                    if not eb.position.is_faculty:
                        to_attendee_final_list.append({
                            'displayName':eb.name,
                            'email':eb.email_nsu,
                        })
                        # to_attendee_final_list.append({
                        #     'displayName':eb.name,
                        #     'email':eb.email_ieee,
                        # })
                for excom in branch_ex_com:
                    to_attendee_final_list.append({
                        'displayName':excom.member.name,
                        'email':excom.member.email_nsu,
                    })
                    # to_attendee_final_list.append({
                    #     'displayName':excom.member.name,
                    #     'email':excom.member.email_ieee,
                    # })
                pass
            elif option=="scag_eb":
                # get all the society, chapters and AG EBS
                for i in range(2,6):
                    get_current_panel_of_sc_ag=SC_AG_Info.get_current_panel_of_sc_ag(request=request,sc_ag_primary=i)
                    if(get_current_panel_of_sc_ag.exists()):
                        ex_com=SC_AG_Info.get_sc_ag_executives_from_panels(request=request,panel_id=get_current_panel_of_sc_ag[0].pk)
                        for ex in ex_com:
                            if ex.member is not None:
                                #If is faculty then skip
                                if not ex.member.position.is_faculty:
                                    to_attendee_final_list.append({
                                        'displayName':ex.member.name,
                                        'email':ex.member.email_nsu,
                                    })
                                    # to_attendee_final_list.append({
                                    #     'displayName':ex.member.name,
                                    #     'email':ex.member.email_ieee,
                                    # })
                            else:
                                to_attendee_final_list.append({
                                    'displayName':ex.ex_member.name,
                                    'email':ex.ex_member.email,
                                })
            elif option[0:9] == "recruits_":
                recruit_id = int(option[9:])
                recruited_mem = recruited_members.objects.filter(session_id = recruit_id)
                for mem in recruited_mem:
                    to_attendee_final_list.append({
                        'displayName':mem.first_name,
                        'email':mem.email_nsu,
                    })
                    # to_attendee_final_list.append({
                    #     'displayName':mem.first_name,
                    #     'email'::mem.email_nsu,
                    # })
            else:
                to_attendee_final_list.append(
                    {
                        'displayName':"Arman M (IEEE)",
                        'email':'arman.mokammel@ieee.org'
                    },
                )
                to_attendee_final_list.append(
                    {
                        'displayName':"Arman M (NSU)",
                        'email':'arman.mokammel@northsouth.edu'
                    },
                )
        
        return to_attendee_final_list

    
    def update_event_google_calendar(request, event_id, publish_event_gc, description, attendeeOption, add_attendee_names, add_attendee_emails, documents):

        event = Events.objects.get(id=event_id)
        event.publish_in_google_calendar = publish_event_gc
        event.event_description_for_gc = description
        event.selected_attendee_list = ""
        for option in attendeeOption:
            event.selected_attendee_list += option
            event.selected_attendee_list += ','

        event.additional_attendees = {}
        for i in range(len(add_attendee_emails)):
            additional_attendees = {
                'displayName':add_attendee_names[i],
                'email':add_attendee_emails[i]
            }
            event.additional_attendees[i] = additional_attendees
        event.save()

        if documents:
            for doc in documents:
                file = CalendarHandler.google_drive_upload_files(request, doc)
                if file:
                    Google_Calendar_Attachments.objects.create(event_id=event, file_id=file['id'] , file_name=file['name'] , file_url=file['webViewLink'])

        documents = Google_Calendar_Attachments.objects.filter(event_id=event_id)

        to_attendee_final_list = []
        if event.publish_in_google_calendar:
            to_attendee_final_list = Branch.get_attendee_list_from_backend(request, attendeeOption)
        
            for attendee,value in event.additional_attendees.items():
                to_attendee_final_list.append(
                    {
                        'displayName':value['displayName'],
                        'email':value['email']
                    }
                ) 

        if(not event.google_calendar_event_id and event.publish_in_google_calendar == True):
            event.google_calendar_event_id = CalendarHandler.create_event_in_calendar(request=request, event_id=event.pk, title=event.event_name, description=event.event_description_for_gc, location="North South University", start_time=event.start_date, end_time=event.end_date, event_link='http://' + request.META['HTTP_HOST'] + reverse('main_website:event_details', args=[event.pk]), attendeeList=to_attendee_final_list, attachments=documents)
            if(not event.google_calendar_event_id):
                event.publish_in_google_calendar = False
                messages.warning(request, "Could not publish event in calendar")
            else:
                messages.success(request, "Event published in calendar")

            event.save()
        elif(event.google_calendar_event_id and event.publish_in_google_calendar == False):
            if(CalendarHandler.delete_event_in_calendar(request, event.google_calendar_event_id)):
                event.google_calendar_event_id = ""
                messages.success(request, "Event deleted from calendar")
            else:
                event.publish_in_google_calendar = True
                messages.warning(request, "Could not delete event from calendar")
            event.save()
        elif(event.google_calendar_event_id):
            if(CalendarHandler.update_event_in_calendar(request, event.google_calendar_event_id, None, event.event_description_for_gc, None, None, to_attendee_final_list)):
                messages.success(request, "Event updated in calendar")
            else:
                messages.warning(request, "Could not update event in calendar")
        
    def add_feedback(event_id, name, email, satisfaction, comment):
        try:
            allowed_values = ['very_satisfied', 'satisfied', 'not_satisfied']
            if satisfaction not in allowed_values:
                return False
            feedback = Event_Feedback(event_id=Events.objects.get(id=event_id), name=name, email=email, satisfaction=satisfaction, comment=comment)
            feedback.save()
            return True
        except:
            return False
        
    def get_all_feedbacks(event_id):
        event_feedbacks = Event_Feedback.objects.filter(event_id=Events.objects.get(id=event_id))

        return event_feedbacks

    # def load_ex_com_panel_list():
    #     panels=Executive_commitee.objects.all().order_by('-pk')
    #     ex_com_panel_list=[]
    #     for committee in panels:
    #         ex_com_panel_list.append(committee)
        
    #     return ex_com_panel_list
    def add_member_to_branch_view_access(request,selected_members):
        logger = logging.getLogger(__name__)

        try:
            for i in selected_members:
                new_member=Branch_Data_Access.objects.create(ieee_id=Members.objects.get(ieee_id=i))
                new_member.save()
            messages.success(request,"Members were added to the View Access Page")
            return True
        except IntegrityError:
            messages.info(request,"The member already exists in the Table. Search to view them.")
        except Exception as ex:
            messages.error(request,"Can not add members.")
            logger.info(ex, exc_info=True)
    
    def update_member_to_branch_view_access(request,ieee_id,**kwargs):
        '''This function updates the view permission of Branch Data Access.
        ****Remember that the passed keys in the keyword arguments must match with the models attributes.
        '''
        try:
            # first get member
            get_member=Branch_Data_Access.objects.get(ieee_id=ieee_id)
            
            # iterate through the fields of the member
            for field in get_member._meta.fields:
                # if field name matches with passed kwargs
                if field.name in kwargs['kwargs']:
                    # set attribute of the member with the value from keyword argument
                    setattr(get_member,field.attname,kwargs['kwargs'][field.name])
                    # save the member
                    get_member.save()
            messages.success(request,f"View Permission was updated for {ieee_id}")
            return True
        except:
            messages.error(request,"View Permission can not be updated!")
        

    def remover_member_from_branch_access(request,ieee_id):
        try:
            Branch_Data_Access.objects.get(ieee_id=ieee_id).delete()
            messages.info(request,f"{ieee_id} was removed from Branch Data access Table")
            return True
        except:
            messages.error(request,"Can not remove member from Branch Data access!")
            return False
    
    def get_branch_data_access(request):
        try:
            return Branch_Data_Access.objects.all()
        except:
            messages.error("Something went wrong while loading Data Access for Branch")
            return False
        
    
    
    def load_branch_eb_panel():
        '''This function loads all the EB panel members from the branch.
        Checks if the position of the member is True for is_eb_member and if member exists in current EB Panel'''
        get_current_panel=Branch.load_current_panel()
        members=Members.objects.all()
        eb_panel=[]
        for member in members:
            if member.position.is_eb_member:
                if (Panel_Members.objects.filter(tenure=get_current_panel.pk,member=member.ieee_id).exists()):
                    eb_panel.append(member)
        return eb_panel
                
    def load_all_officers_of_branch():
        '''This function loads all the officer members from the branch.
        Checks if the position of the member is True for is_officer and if he belongs from the current active panel'''
        get_current_panel=Branch.load_current_panel()
        members=Members.objects.all()
        branch_officers=[]
        for member in members:
            if member.position.is_officer:
                if (Panel_Members.objects.filter(tenure=get_current_panel.pk,member=member.ieee_id).exists()):
                    branch_officers.append(member)
        return branch_officers
    
    def load_all_active_general_members_of_branch():
        '''This function loads all the general members from the branch whose memberships are active
        '''
        members=Members.objects.all()
        general_members=[]
        
        for member in members:
           
            if (MDT_DATA.get_member_account_status(ieee_id=member.ieee_id)):
                
                if(member.position.id==13):
                    
                    general_members.append(member)
        return general_members
    
    def load_all_active_members_of_branch():
        '''This function loads all the members from the branch whose memberships are active
        '''
        all_members=Members.objects.all()
        members=[]
        
        for member in all_members:
           
            if (MDT_DATA.get_member_account_status(ieee_id=member.ieee_id)):                
                members.append(member)

        return members
    
    def create_panel(request,tenure_year,current_check,panel_start_date,panel_end_date):
        '''This function creates a panel object. Collects parameter value from views '''
        try:
            # Check if the panel being created is the current panel
            if(current_check is None):
                # Create with current_check=False
                new_panel=Panels.objects.create(year=tenure_year,creation_time=panel_start_date,current=False,panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=1),panel_end_time=panel_end_date) #primary=1 as this is branch's panel
                new_panel.save()
                messages.success(request,"Panel was created successfully")
                return True
            else:
                # If the panel being created is current
                # Changing previous panel current status to False
                Panels.objects.filter(current=True).update(current=False)
                # Create with current_check=True
                new_panel=Panels.objects.create(year=tenure_year,creation_time=panel_start_date,current=True,panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=1),panel_end_time=panel_end_date) #primary=1 as this is branch's panel)
                new_panel.save()
                messages.success(request,"Panel was created successfully")
                messages.info(request,"Current Panel has been changed!")
                return True
        except sqlite3.OperationalError: #if no such table exists
            messages.error(request,"No Data Table found!")
            return False
        except: 
            messages.error(request,"Some error occured! Try again.")
            return False
    
    def delete_panel(request,panel_id):
        ''' This function deletes a panel and makes all its members a general member and team = None'''

        get_panel=Panels.objects.get(pk=panel_id)
        
        get_panel_members=Panel_Members.objects.filter(tenure=panel_id)
        
        for i in get_panel_members:
            # make all the members general members first and then team=None
            try:
                Members.objects.filter(ieee_id=i.member.ieee_id).update(position=Roles_and_Position.objects.get(id=13),team=None)
                i.delete()
            except:
                messages.error(request,"Something went wrong while deleting members from the panel")

        # deleting the panel
        try:
            get_panel.delete()
            messages.info(request,"Panel deleted successfully.")
            return True
        except:
            messages.error(request,'Can not delete this panel. Something went wrong!')
            return False
        
    def change_panel_member_position_and_team_none_in_branch(request,panel_id):
        '''This function finds the members in a panel and makes their Position and team None
        in the SC_AG_Members Table when required.'''
        try:
            get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=panel_id))
            for member in get_panel_members:
                if(member.member is not None):
                    Members.objects.filter(ieee_id=member.member.ieee_id).update(position=Roles_and_Position.objects.get(id=13),team=None)
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def update_panel_settings(request,panel_id,panel_tenure,is_current_check,panel_start_date,panel_end_date):
        '''This function updates the panel settings and makes changes according to it'''
        try:
            # get the panel
            panel_to_update=Panels.objects.get(id=panel_id)
            # first check if the user wants to make a non current panel to current
            if(is_current_check and (panel_to_update.current==False)):
                # find panels which are current now and make them false
                previous_current_panel=Panels.objects.filter(panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=1),current=True)
                if(previous_current_panel.exists()):
                    # Update the Position,Team of Branch members in that panel as None
                    for panel in previous_current_panel:
                        if(Branch.change_panel_member_position_and_team_none_in_branch(request=request,panel_id=panel.pk)):
                            # set the current value of Panel to False
                            panel.current=False
                            panel.save()
                        else:
                            return False
                # now get the members of the panel and update their team and Position in INSB members Table
                members_in_panel=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=panel_id))
                for member in members_in_panel:
                    if(member.member is not None):
                        if member.team is None:
                            # update team as none
                            Members.objects.filter(ieee_id=member.member.ieee_id).update(team=None,position=Roles_and_Position.objects.get(id=member.position.id))                
                        else:
                            Members.objects.filter(ieee_id=member.member.ieee_id).update(team=Teams.objects.get(primary=member.team.primary),position=Roles_and_Position.objects.get(id=member.position.id))
                #now update the panel
                panel_to_update.current=True
                panel_to_update.year=panel_tenure
                panel_to_update.creation_time=panel_start_date
                panel_to_update.panel_end_time=panel_end_date
                panel_to_update.save()
                messages.success(request,"Panel Information was updated!")
                return True
            # then we check if we are making a current panel to a non current panel.
            elif(not is_current_check and panel_to_update.current):
                # Make positions and Teams of Members of that panel as None
                if(Branch.change_panel_member_position_and_team_none_in_branch(request=request,panel_id=panel_to_update.pk)):
                    panel_to_update.current=False
                    panel_to_update.year=panel_tenure
                    panel_to_update.creation_time=panel_start_date
                    panel_to_update.panel_end_time=panel_end_date
                    panel_to_update.save()
                    messages.success(request,"Panel Information was updated!")
                    return True
                else:
                    return False
            else:
                # for all other instances update normally
                panel_to_update.current=is_current_check
                panel_to_update.year=panel_tenure
                panel_to_update.creation_time=panel_start_date
                panel_to_update.panel_end_time=panel_end_date
                panel_to_update.save()
                messages.success(request,"Panel Information was updated!")
                return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not Update Panel. Something went wrong!")
            return False
            

    def load_panel_by_id(panel_id):
        '''This loads all the select panel's information from Panels table'''
        try:
            panel = Panels.objects.get(id=panel_id)
            return panel
        except:
            raise Http404("The requested page does not exist.")
    
    def get_panel_by_year(panel_year):
        '''This returns the panel by year'''
        try:
            panel=Panels.objects.filter(year=panel_year).first()
            return panel
        except:
            raise Http404("The requested page does not exist.")
        
    def load_current_panel_members():
        current_panel = Branch.load_current_panel()
        current_panel_members = Branch.load_panel_members_by_panel_id(panel_id=current_panel)
        return current_panel_members

    
    def load_panel_members_by_panel_id(panel_id):
        '''This load all the info associated with a panel from Panel members Table'''
        try:
            get_panel_members=Panel_Members.objects.filter(tenure=panel_id).all()
            return get_panel_members
        except:
            raise Http404("The requested page does not exist.")
    
                                
    def load_all_panels():
        '''This function loads all the panels from the database'''
        try:
            panels=Panels.objects.filter(panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=1)).order_by('-current','-year')
            return panels
        except:
            return DatabaseError

    def load_current_panel():
        '''This method loads the current panel of Branch. returns the year of the panel'''
        currentPanel=Panels.objects.filter(current=True,panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=1))
        return currentPanel.first()
        
    def load_roles_and_positions():
        '''This methods all the Position for Branch Only'''
        getBranchId=Branch.getBranchID()
        positions=Roles_and_Position.objects.filter(role_of=getBranchId.pk)
        return positions
    def load_all_insb_members():
        insb_members=Members.objects.all().order_by('nsu_id')
        return insb_members
    
    def add_member_to_team(ieee_id,team_primary,position):
        '''This function adds member to the team'''
        getTeam=Teams.objects.get(primary=team_primary)
        # Assign positions according to Panels
        getCurrentPanel=Branch.load_current_panel()
        team=getTeam.id
        if(getCurrentPanel is not None):
            try:
                if(team_primary==7): #Checking if the team is MDT as its id is 7. this is basically done for the data access which is not necessary to do for every team.
                    
                    Members.objects.filter(ieee_id=ieee_id).update(team=team,position=position)
                    try:
                        # check if Member existed in the current panel
                        check_member=Panel_Members.objects.filter(tenure=Panels.objects.get(id=getCurrentPanel.pk),member=ieee_id).exists()
                        if(check_member):
                            # updating position and team for the member
                            Panel_Members.objects.filter(tenure=Panels.objects.get(id=getCurrentPanel.pk),member=ieee_id).update(position=Roles_and_Position.objects.get(id=position),team=Teams.objects.get(primary=team_primary))
                        
                        else:
                            # add member in the Current panel
                            new_member_in_panel=Panel_Members.objects.create(tenure=Panels.objects.get(id=getCurrentPanel.pk),member=Members.objects.get(ieee_id=ieee_id),
                                                                            position=Roles_and_Position.objects.get(id=position),team=Teams.objects.get(id=team))
                            new_member_in_panel.save()
                    except:
                        return DatabaseError

                    return True
                else:
                    Members.objects.filter(ieee_id=ieee_id).update(team=team,position=position)
                    try:
                        # check if member existed in the current panel
                        check_member=Panel_Members.objects.filter(tenure=Panels.objects.get(id=getCurrentPanel.pk),member=ieee_id).exists()
                        if(check_member):
                            # updating position and team for the member
                            Panel_Members.objects.filter(tenure=Panels.objects.get(id=getCurrentPanel.pk),member=ieee_id).update(position=Roles_and_Position.objects.get(id=position),team=Teams.objects.get(primary=team_primary))
                        else:
                            # add member to current panel
                            new_member_in_panel=Panel_Members.objects.create(tenure=Panels.objects.get(id=getCurrentPanel.pk),member=Members.objects.get(ieee_id=ieee_id),
                                                                            position=Roles_and_Position.objects.get(id=position),team=Teams.objects.get(id=team))
                            new_member_in_panel.save()
                    except:
                        return DatabaseError
                    return True
            except Members.DoesNotExist:
                return False
            except:
                return DatabaseError
        else:
            return None
        
    def load_all_events():
        return Events.objects.all().order_by('-start_date','-event_date')
    
    def load_all_inter_branch_collaborations_with_events(primary):
        '''This fuction returns a dictionary with key as events id and values as a list of inter collaborations 
            for that specific event'''
        try:
            dic = {}
            collaborations=[]
            if primary == 1:
                events = Branch.load_all_events()
            else:
                events = Branch.load_all_events_for_groups(primary)
                
            for i in events:
                all_collaborations_for_this_event = InterBranchCollaborations.objects.filter(event_id = i.id)
                for j in all_collaborations_for_this_event:
                    collaborations.append(j.collaboration_with.group_name)  
                dic.update({i:collaborations})
                collaborations=[]
                
            return dic
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Can not load intercollaboration details for each events. Something went wrong!")
            return False

    def events_not_registered_to_mega_events(events_list):

        '''This function returns only those events with collaboration those are not associated
            with any mega events'''
        try:
            dic = {}
            for key,value in events_list.items():

                if key.super_event_id  is None or key.super_event_id == 0:
                    dic[key] = value

            return dic
        
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Can not load intercollaboration details for each events. Something went wrong!")
            return False

    def load_event_published(event_id):
        '''This function will return wheather the event is published or not'''

        return Events.objects.get(id = event_id).publish_in_main_web
    
    def load_event_published_gc(event_id):
        '''This function will return wheather the event is published in google calendar or not'''

        return Events.objects.get(id = event_id).publish_in_google_calendar
    
    def is_flagship_event(event_id):

        '''This function will return wheather the event is flagship or not'''

        return Events.objects.get(id = event_id).flagship_event
    
    def is_featured_event(event_id):

        '''This function will return wheater the event is featured or not'''

        return Events.objects.get(id = event_id).is_featured
    
    def is_registration_fee_required(event_id):
        
        '''This function will return wheather the event requires any regsitration fee or not'''

        return Events.objects.get(id=event_id).registration_fee
    
    def publish_event(event_id,state):
        '''This function will publish or unpublish the event'''
        try:
            event = Events.objects.get(id=event_id)
            if state == "on":
                event.publish_in_main_web = True
            else:
                event.publish_in_main_web= False
            event.save()
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Could not publish/unpublish the event. Something went wrong!")

    def button_status(state):

        '''This function returns the status of the toggle button '''

        if state == None:
            return False
        else:
            return True

    def load_all_mother_events():
        '''This method loads all the mother/Super events'''
        return SuperEvents.objects.all().order_by('-pk')
    def load_all_inter_branch_collaboration_options():
        '''This loads all the chapters and Societies of the branch'''
        return Chapters_Society_and_Affinity_Groups.objects.all().order_by('primary')
    
    def load_all_event_type_for_groups(primary):

        '''This function loads all event type for the specific group'''

        return Event_Category.objects.filter(event_category_for = Chapters_Society_and_Affinity_Groups.objects.get(primary = primary))
    
    def load_all_events_for_groups(primary):

        '''This function will return a list of only those events associated with that particular group'''
        events = Events.objects.filter(event_organiser= Chapters_Society_and_Affinity_Groups.objects.get(primary=primary))
        collaborations_list = InterBranchCollaborations.objects.filter(collaboration_with=Chapters_Society_and_Affinity_Groups.objects.get(primary=primary)).values_list('event_id')
        events_with_collaborated_events = events.union(Events.objects.filter(pk__in=collaborations_list))
        return events_with_collaborated_events.order_by('-start_date','-event_date')
        
    
    def event_page_access(request):

        '''function for acceessing particular memebers into event page through
        portal'''

        try:
            user = request.user
            user_id = user.username
            member = Members.objects.get(ieee_id=int(user_id))
            roles_and_positions = Roles_and_Position.objects.get(id = member.position.id)
            if roles_and_positions.is_eb_member:
                return True
            else:
                return False
        except:
            
            '''Super users and staff users can access'''

            has_access= Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username)
            return has_access
    
    def event_interBranch_Collaborations(event_id):
        '''this function loads all the Inter Branch Collaborations from the database. cross match with event_id'''

        interBranchCollaborations=InterBranchCollaborations.objects.filter(event_id=Events.objects.get(id=event_id))

        return interBranchCollaborations

    def event_IntraBranch_Collaborations(event_id):
        '''this function loads all the Intra Branch Collaborations from the database. cross match with event_id'''
        
        intraBranchCollaborations=IntraBranchCollaborations.objects.filter(event_id=Events.objects.get(id=event_id))
        if(intraBranchCollaborations.count() == 0):
            return ""
        else:
            intraBranchCollaborations = IntraBranchCollaborations.objects.get(event_id=Events.objects.get(id=event_id))
            return intraBranchCollaborations
    
    def load_insb_organised_events():
        
        return Events.objects.filter(event_organiser=5).order_by('-start_date','-event_date')
    

    def delete_event(request, event_id):
        ''' This function deletes event from database '''
        try:
            #Getting the event instance
            event = Events.objects.get(id = event_id)

            if(event.google_calendar_event_id):
                CalendarHandler.delete_event_in_calendar(request, event.google_calendar_event_id)

            if(NotificationHandler.delete_notification(notification_type=Branch.event_notification_type, notification_of=event)):
                messages.success(request, "Notifications of the event deleted successfully!")
            else:
                messages.warning(request, "Could not delete notifications of the event!")
                return False

            try:
                #getting banner image of the image and deleting it from if exists
                graphics_image = Graphics_Banner_Image.objects.get(event_id = event)
                image_path=settings.MEDIA_ROOT+str(graphics_image.selected_image)
                if os.path.isfile(image_path):
                    os.remove(image_path)
            except:
                pass
            #getting media images of the event and deleting file from os
            media_images = Media_Images.objects.filter(event_id = event)

            for image in media_images:
                img_path = settings.MEDIA_ROOT + str(image.selected_images)
                if os.path.exists(img_path):
                    os.remove(img_path)
            
            content_files = Content_Team_Document.objects.filter( event_id = event)
            #getting content files from  db and removing them physically from server directory
            for file in content_files:
                doc_path = settings.MEDIA_ROOT + str(file.document)
                if os.path.exists(doc_path):
                    os.remove(doc_path)

            attachments = Google_Calendar_Attachments.objects.filter(event_id=event)
            for attachment in attachments:
                Branch.delete_attachment(request, attachment.pk)
            #deleting the event along with its  related data from DB
            event.delete()
            return True
        except:
            return False
        
    def set_about_ieee_page(about_details, learn_more_link, mission_and_vision_link, community_details, start_with_ieee_details, collaboration_details,
                                publications_details, events_and_conferences_details, achievements_details, innovations_and_developments_details,
                                students_and_member_activities_details, quality_details, join_now_link, asia_pacific_link, ieee_computer_organization_link,
                                customer_service_number, presidents_names, founders_names, about_image, community_image,
                                innovations_and_developments_image, students_and_member_activities_image, quality_image):
        ''' This function saves all data for about_ieee page to database, except for external links added through '+' button '''
        
        try:
            about_ieee, created = About_IEEE.objects.get_or_create(id=1)
            about_ieee.about_ieee=about_details
            about_ieee.learn_more_link=learn_more_link
            about_ieee.mission_and_vision_link=mission_and_vision_link
            about_ieee.community_description=community_details
            about_ieee.start_with_ieee_description=start_with_ieee_details
            about_ieee.collaboration_description=collaboration_details
            about_ieee.publications_description=publications_details
            about_ieee.events_and_conferences_description=events_and_conferences_details
            about_ieee.achievements_description = achievements_details
            about_ieee.innovations_and_developments_description=innovations_and_developments_details
            about_ieee.students_and_member_activities_description=students_and_member_activities_details
            about_ieee.quality_description=quality_details
            about_ieee.about_image=about_image
            about_ieee.community_image=community_image
            about_ieee.innovations_and_developments_image=innovations_and_developments_image
            about_ieee.students_and_member_activities_image=students_and_member_activities_image
            about_ieee.quality_image=quality_image
            about_ieee.join_now_link=join_now_link
            about_ieee.asia_pacific_link=asia_pacific_link
            about_ieee.ieee_computer_organization_link=ieee_computer_organization_link
            about_ieee.customer_service_number=customer_service_number
            about_ieee.presidents_names=presidents_names
            about_ieee.founders_names=founders_names

            about_ieee.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def set_ieee_bangladesh_section_page(about_details, ieeebd_link, members_and_volunteers_details, benefits_details,
                                            student_branches_details, affinity_groups_details, communty_and_society_details,
                                            achievements_details, chair_name, chair_email, secretary_name,
                                            secretary_email, office_secretary_name, office_secretary_number, about_image, members_and_volunteers_image):
        ''' This function saves all data for about_ieee_bangladesh_section page to database, except for external links added through '+' button '''

        try:
            ieee_bangladesh_section, created = IEEE_Bangladesh_Section.objects.get_or_create(id=1)
            ieee_bangladesh_section.about_ieee_bangladesh = about_details
            ieee_bangladesh_section.ieee_bangladesh_logo = about_image
            ieee_bangladesh_section.ieee_bd_link = ieeebd_link
            ieee_bangladesh_section.member_and_volunteer_description = members_and_volunteers_details
            ieee_bangladesh_section.member_and_volunteer_picture = members_and_volunteers_image
            ieee_bangladesh_section.benefits_description = benefits_details
            ieee_bangladesh_section.student_branches_description = student_branches_details
            ieee_bangladesh_section.affinity_groups_description = affinity_groups_details
            ieee_bangladesh_section.community_and_society_description = communty_and_society_details
            ieee_bangladesh_section.achievements_description = achievements_details
            ieee_bangladesh_section.chair_name = chair_name
            ieee_bangladesh_section.chair_email = chair_email
            ieee_bangladesh_section.secretary_name = secretary_name
            ieee_bangladesh_section.secretary_email = secretary_email
            ieee_bangladesh_section.office_secretary_name = office_secretary_name
            ieee_bangladesh_section.office_secretary_number = office_secretary_number

            ieee_bangladesh_section.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def set_ieee_nsu_student_branch_page(about_nsu_student_branch, chapters_description, ras_read_more_link,
                                            pes_read_more_link, ias_read_more_link, wie_read_more_link, creative_team_description,
                                            mission_description, vision_description, events_description, join_now_link, achievements_description,
                                            about_image,ras_image,pes_image,ias_image,wie_image,mission_image,vision_image):
        ''' This function saves all data for about_ieee_nsu_student_branch page to database, except for external links added through '+' button '''        
        
        try:
            ieee_nsu_student_branch, created = IEEE_NSU_Student_Branch.objects.get_or_create(id=1)
            ieee_nsu_student_branch.about_nsu_student_branch = about_nsu_student_branch
            ieee_nsu_student_branch.about_image = about_image
            ieee_nsu_student_branch.chapters_description = chapters_description
            ieee_nsu_student_branch.ras_read_more_link = ras_read_more_link
            ieee_nsu_student_branch.ras_image = ras_image
            ieee_nsu_student_branch.pes_read_more_link = pes_read_more_link
            ieee_nsu_student_branch.pes_image = pes_image
            ieee_nsu_student_branch.ias_read_more_link = ias_read_more_link
            ieee_nsu_student_branch.ias_image = ias_image
            ieee_nsu_student_branch.wie_read_more_link = wie_read_more_link
            ieee_nsu_student_branch.wie_image = wie_image
            ieee_nsu_student_branch.creative_team_description = creative_team_description
            ieee_nsu_student_branch.mission_description = mission_description
            ieee_nsu_student_branch.mission_image = mission_image
            ieee_nsu_student_branch.vision_description = vision_description
            ieee_nsu_student_branch.vision_image = vision_image
            ieee_nsu_student_branch.events_description = events_description
            ieee_nsu_student_branch.join_now_link = join_now_link
            ieee_nsu_student_branch.achievements_description = achievements_description

            ieee_nsu_student_branch.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def set_ieee_region_10_page(ieee_region_10_description,ieee_region_10_history_link,young_professionals_description,women_in_engineering_ddescription,
                                    student_and_member_activities_description,educational_activities_and_involvements_description,industry_relations_description,
                                    membership_development_description,events_and_conference_description,home_page_link,website_link,membership_inquiry_link,
                                    for_volunteers_link,contact_number,ieee_region_10_image,young_professionals_image,membership_development_image,
                                    background_picture_parallax,events_and_conference_image):
        ''' This function saves all data for about_ieee_region_10 page to database, except for external links added through '+' button '''
        
        try:
            ieee_region_10, created = IEEE_Region_10.objects.get_or_create(id=1)
            ieee_region_10.ieee_region_10_description = ieee_region_10_description
            ieee_region_10.ieee_region_10_history_link = ieee_region_10_history_link
            ieee_region_10.young_professionals_description = young_professionals_description
            ieee_region_10.women_in_engineering_ddescription = women_in_engineering_ddescription
            ieee_region_10.student_and_member_activities_description =student_and_member_activities_description
            ieee_region_10.educational_activities_and_involvements_description = educational_activities_and_involvements_description
            ieee_region_10.industry_relations_description = industry_relations_description
            ieee_region_10.membership_development_description = membership_development_description
            ieee_region_10.events_and_conference_description = events_and_conference_description
            ieee_region_10.home_page_link = home_page_link
            ieee_region_10.website_link = website_link
            ieee_region_10.membership_inquiry_link = membership_inquiry_link
            ieee_region_10.for_volunteers_link = for_volunteers_link
            ieee_region_10.contact_number = contact_number
            ieee_region_10.ieee_region_10_image = ieee_region_10_image
            ieee_region_10.young_professionals_image = young_professionals_image
            ieee_region_10.membership_development_image = membership_development_image
            ieee_region_10.background_picture_parallax = background_picture_parallax
            ieee_region_10.events_and_conference_image = events_and_conference_image

            ieee_region_10.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def checking_length(*descriptions):
        '''This function checks the length of the description fields. If any one exceed 2000 or if any one is
            empty then data won't be saved.'''
        
        try:
            #assinging checking length
            max_length = 2000

            for description in descriptions:
                #removing html tags to check true length of each fields
                filtered_description = Branch.process_ckeditor_content(description)
                #checking to see the length. Returns true if length is more than 700 or is 0
                if(len(filtered_description)> max_length or len(filtered_description) == 0):
                    return True
                
            return False
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def about_ieee_delete_image(image_id,image_path):
        ''' This function deletes an image from the about_ieee database. It takes an image_id(category) and image_path as parameter '''

        try:
            about_ieee = About_IEEE.objects.get(id=1)
            #getting the path of the image from the filesystem
            path = settings.MEDIA_ROOT+str(image_path)
            #checking to see if the image exists in filesytem. If yes then delete it from filesystem
            if os.path.exists(path):
                os.remove(path)

            #checking to see which image is requested to be deleted
            if(image_id == 'about_image'):
                about_ieee.about_image = None
            elif(image_id == 'community_image'):
                about_ieee.community_image = None
            elif(image_id == 'innovations_and_developments_image'):
                about_ieee.innovations_and_developments_image = None
            elif(image_id == "students_and_member_activities_image"):
                about_ieee.students_and_member_activities_image = None
            elif(image_id == "quality_image"):
                about_ieee.quality_image = None

            #saving before returning
            about_ieee.save()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def ieee_bangladesh_section_page_delete_image(image_id,image_path):
        ''' This function deletes an image from the ieee_bangladesh_section database. It takes an image_id(category) and image_path as parameter '''

        try:
            ieee_bangladesh_section = IEEE_Bangladesh_Section.objects.get(id=1)
            #getting the path of the image from the local machine
            path = settings.MEDIA_ROOT+str(image_path)

            #checking to see if the image exists in filesytem. If yes then delete it from filesystem
            if os.path.exists(path):
                os.remove(path)

            #checking to see which image is requested to be deleted
            if(image_id == 'ieee_bangladesh_logo'):
                ieee_bangladesh_section.ieee_bangladesh_logo = None
            elif(image_id == 'member_and_volunteer_picture'):
                ieee_bangladesh_section.member_and_volunteer_picture = None
            
            #saving before returning
            ieee_bangladesh_section.save()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def ieee_nsu_student_branch_page_delete_image(image_id,image_path):
        ''' This function deletes an image from the ieee_nsu_student_branch database. It takes an image_id(category) and image_path as parameter '''

        try:
            ieee_nsu_student_branch = IEEE_NSU_Student_Branch.objects.get(id=1)
            #getting the path of the image from the local machine
            path = settings.MEDIA_ROOT+str(image_path)
            
            #checking to see if the image exists in filesytem. If yes then delete it from filesystem
            if os.path.exists(path):
                os.remove(path)

            #checking to see which image is requested to be deleted
            if(image_id == 'about_image'):
                ieee_nsu_student_branch.about_image = None
            elif(image_id == 'ras_image'):
                ieee_nsu_student_branch.ras_image = None
            elif(image_id == 'pes_image'):
                ieee_nsu_student_branch.pes_image = None
            elif(image_id == 'ias_image'):
                ieee_nsu_student_branch.ias_image = None
            elif(image_id == 'wie_image'):
                ieee_nsu_student_branch.wie_image = None
            elif(image_id == 'mission_image'):
                ieee_nsu_student_branch.mission_image = None
            elif(image_id == 'vision_image'):
                ieee_nsu_student_branch.vision_image = None
            
            #saving before returning
            ieee_nsu_student_branch.save()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def ieee_region_10_page_delete_image(image_id,image_path):
        ''' This function deletes an image from the ieee_region_10 database. It takes an image_id(category) and image_path as parameter '''

        try:
            ieee_region_10 = IEEE_Region_10.objects.get(id=1)
            path = settings.MEDIA_ROOT+str(image_path)

            if os.path.exists(path):
                os.remove(path)

            if(image_id == 'ieee_region_10_picture'):
                ieee_region_10.ieee_region_10_image = None
            elif(image_id == 'young_professionals_picture'):
                ieee_region_10.young_professionals_image = None
            elif(image_id == 'membership_development_picture'):
                ieee_region_10.membership_development_image = None
            elif(image_id == 'background_picture'):
                ieee_region_10.background_picture_parallax = None
            elif(image_id == 'events_and_conference_picture'):
                ieee_region_10.events_and_conference_image = None

            #saving before returning
            ieee_region_10.save()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def process_ckeditor_content(ckeditor_html):
        # Parse the HTML content with Beautiful Soup
        soup = BeautifulSoup(ckeditor_html, 'html.parser')

        # Extract the text content without HTML tags
        text_content = soup.get_text()

        # Now, 'text_content' contains only the actual content without HTML tags
        return text_content
    
    def add_about_page_link(page_title, category, title, link):
        ''' This function adds a new page link. Used in About pages. It takes a page_title, category, title and link as parameter '''

        try:
            page_link = Page_Link.objects.create(page_title=page_title, category=category, title=title, link=link)
            page_link.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def update_about_page_link(link_id, page_title, title, link):
        ''' This function updates a page link. Used in About pages. It takes a link_id, page_title, category, title and link as parameter '''

        try:
            page_link = Page_Link.objects.get(id=link_id, page_title=page_title)
            page_link.title = title
            page_link.link = link
            page_link.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def remove_about_page_link(link_id, page_title):
        ''' This function deletes a page link. Used in About pages. It takes a link_id and page_title as parameter '''

        try:
            Page_Link.objects.get(id=link_id, page_title=page_title).delete()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def get_about_page_links(page_title):
        ''' This function returns all page links for a specific page. Used in About pages. It takes a page_title as parameter.
            It returns a dictionary where category is the key and value is an array of page_link '''

        try:
            #Getting all links for a specific page and ordering by primary key
            page_links_all = Page_Link.objects.filter(page_title=page_title).order_by('pk')
            page_links_dict = {}
            categories = []

            #Find all the categories and put them in the categories array
            for page_link in page_links_all:
                #Checking for duplicate entry
                if(page_link.category not in categories):
                    categories.append(page_link.category)
            
            #For each category in the categories array, find all the page links it contains
            for category in categories:
                values = []
                for page_link in page_links_all:
                    #If the category matches
                    if page_link.category == category:
                        #Add the page_link to the values array
                        values.append(page_link)
                #After finding all page_links for a category, create a new key(category) and value(page_link array) and add them to the dictionary
                page_links_dict.update({category : values})
            return page_links_dict
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def save_category_of_faq(title):
        
        '''This function saves the title of the new category FAQ in the database'''

        try:
            #creating the title object
            save_title = FAQ_Question_Category.objects.create(title = title)
            #saving it in database
            save_title.save()

            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def get_all_category_of_questions():

        '''This function returns all the titles registered in database for FAW'''

        try:
            #getting all the titles and returning them
            return FAQ_Question_Category.objects.all().order_by('id')
        
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    def get_saved_questions_and_answers():
        
        '''This function returns a dictionary of all categories of question as key and
            the value containts the list of that categories question and answer objects'''
        
        try:
            #initiazlizing empty dictionary
            dic={}
            #getting all the categories of question using function
            all_categories = Branch.get_all_category_of_questions()
            #iterating over each category 
            for category in all_categories:
                #getting the question and answers of that particular category
                question_answer_list = FAQ_Questions.objects.filter(title = category).order_by('pk')
                #updating dictionart
                #checking if list length is 0 
                if len(question_answer_list) == 0:
                    dic[category] = None
                else:
                    dic[category] = question_answer_list
            #returning the dictionary
            return dic
        
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def update_question_answer(id,title,question_list,answer_list):

        '''This function updates the question and answer for the specified category'''

        try:
            #getting the question category
            cat_obj = FAQ_Question_Category.objects.get(pk=id)
            #getting all titles 
            all_faq = FAQ_Questions.objects.filter(title = cat_obj)
            #deleting all the questions under this category from database
            for i in all_faq:
                i.delete()
            #updating title if changed
            cat_obj.title = title
            cat_obj.save()
            #saving them again in database with updated values and new ones
            for i in range(len(question_list)):
                faq = FAQ_Questions.objects.create(title = cat_obj,question = question_list[i],
                                                   answer = answer_list[i])
                #saving it
                faq.save()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def delete_question_answer(id,q_id):

        '''this function removes the specific question and answer that the user requested for
            a category'''
        
        try:
            #getting the question category
            cat_obj = FAQ_Question_Category.objects.get(pk=id)
            #getting the question and answer
            q_answer = FAQ_Questions.objects.get(title = cat_obj,id = q_id)
            q_answer.delete()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def delete_faq_category(id):

        '''This function deletes the entire category of FAQ'''

        try:
            #getting the object of particular category and deleting it
            faq = FAQ_Question_Category.objects.get(id=id)
            faq.delete()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def save_homepage_thoughts(author,thought):

        '''This function saves the thoughts that the author gave on portal to display on main
            web page'''
        
        try:
            #saving them in database
            homepage_thought = HomePage_Thoughts.objects.create(author = author, quote = thought)
            homepage_thought.save()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def get_all_homepage_thoughts():

        '''This function returns all the thoughts registered in database'''

        try:
            #returning all the thoughts as a list
            return HomePage_Thoughts.objects.all().order_by('pk')
        
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def update_saved_thoughts(author,thought,id):

        '''This function updates the registerd thoughts'''

        try:
            #getting the object from id and updating it with new data
            homepage_thought = HomePage_Thoughts.objects.get(id=id)
            homepage_thought.quote = thought
            homepage_thought.author = author
            homepage_thought.save()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def delete_thoughts(id):
        
        '''This function deletes the thought from the database'''

        try:
            #getting the object from id and deleting it
            homepage_thought = HomePage_Thoughts.objects.get(id=id)
            homepage_thought.delete()
            return True

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False  
        
    def update_profile_picture(picture,ieee_id):

        '''This function updates the profile picture of user'''
        try:
            get_user=Members.objects.get(ieee_id = ieee_id)
            #get the previous profile picture of the user to delete it
            previous_profile_picture=settings.MEDIA_ROOT+str(get_user.user_profile_picture)
            if os.path.isfile(previous_profile_picture):
                #removing previous one from system
                os.remove(previous_profile_picture)
                #saving new one
                get_user.user_profile_picture = picture
                get_user.save()
            else:
                get_user.user_profile_picture = picture
                get_user.save()

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def save_ieee_bangladesh_section_images(image_list):

        '''This function saves the images to the database'''

        try:
            #iterating through image list and saving them
            for image in image_list:

                #creating image object and saving one image at a time
                Image = IEEE_Bangladesh_Section_Gallery.objects.create(picture = image)
                Image.save()

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def get_all_ieee_bangladesh_section_images():

        '''This function returns all images of IEEE Bangladesh Section as list if there is any'''
        try:
            return IEEE_Bangladesh_Section_Gallery.objects.all()
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def delete_ieee_bangladesh_section_gallery_image(id):

        '''This function deletes the image from the database and os'''

        try:
            #deleting the file from the system and the model 
            image = IEEE_Bangladesh_Section_Gallery.objects.get(id=id)
            path = settings.MEDIA_ROOT+str(image.picture)
            os.remove(path)
            image.delete()

            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    def get_mega_event(mega_event_id,primary):

        '''This function returns the mega_event'''

        try:
            return SuperEvents.objects.get(id = mega_event_id,mega_event_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=primary))

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def add_events_to_mega_event(event_list,mega_event):

        '''This function add the events to the mega events'''

        try:
            for i in event_list:
                #getting that event object and assigning it to that specific mega event
                event = Events.objects.get(id = i)
                #assigning event to that mega event
                event.super_event_id = mega_event
                #saving the event
                event.save()
            return True
        
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def get_events_of_mega_event(mega_event):

        '''This function returns all the events of the specific mega event'''

        try:

            return Events.objects.filter(super_event_id = mega_event)

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    def delete_event_from_mega_event(id):
        
        '''This function removes the event from the mega event'''

        try:
            #retriving the specific event and setting its super_event_id to none
            event = Events.objects.get(pk = id)
            event.super_event_id = None
            event.save()
            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
       
    def update_website_homepage_top_banner(pk, banner_image, first_layer_text, first_layer_text_colored, third_layer_text, button_text, button_url):
        try:
            homepage_top_banner = HomePageTopBanner.objects.get(id=pk)

            if(banner_image):
                img_path = settings.MEDIA_ROOT + str(homepage_top_banner.banner_picture)
                if os.path.exists(img_path):
                    os.remove(img_path)
                homepage_top_banner.banner_picture = banner_image

            homepage_top_banner.first_layer_text = first_layer_text
            homepage_top_banner.first_layer_text_colored = first_layer_text_colored
            homepage_top_banner.third_layer_text = third_layer_text
            homepage_top_banner.button_text = button_text
            homepage_top_banner.button_url = button_url

            homepage_top_banner.save()

            return True
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    def get_event_years(primary):

        '''This function returns the events year along with collaborated event years'''
        try:
            #if of branch then no need to check for collaborations
            if primary == 1:
                all_events = Events.objects.all()
            #checking for collaborations
            else:
                events = Events.objects.filter(event_organiser= Chapters_Society_and_Affinity_Groups.objects.get(primary=primary))
                collaborations_list = InterBranchCollaborations.objects.filter(collaboration_with=Chapters_Society_and_Affinity_Groups.objects.get(primary=primary)).values_list('event_id')
                all_events = events.union(Events.objects.filter(pk__in=collaborations_list))
            #getting all the years
            unique_years = []
            for event in all_events:
                if event.event_date:
                    if event.event_date.year not in unique_years:
                        unique_years.append(event.event_date.year)
            #sorting it
            unique_years.sort(reverse=True)
            return unique_years

        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def load_all_inter_branch_collaborations_with_events_yearly(year,primary):
        
        '''This fuction returns a dictionary with key as events id and values as a list of inter collaborations 
            for that specific event yearly'''
        try:
            dic = {}
            collaborations=[]
            if primary == 1 :
                final_events = Events.objects.filter(event_date__year = year)
            else:
                events = Events.objects.filter(event_date__year = year,event_organiser = Chapters_Society_and_Affinity_Groups.objects.get(primary = primary))
                collaborations_list = InterBranchCollaborations.objects.filter(collaboration_with=Chapters_Society_and_Affinity_Groups.objects.get(primary=primary)).values_list('event_id')
                events_with_collaborated_events = events.union(Events.objects.filter(pk__in=collaborations_list,event_date__year = year))
                final_events = events_with_collaborated_events.order_by('-event_date')
           
            for i in final_events:
                all_collaborations_for_this_event = InterBranchCollaborations.objects.filter(event_id = i.id)
                for j in all_collaborations_for_this_event:
                    collaborations.append(j.collaboration_with.group_name)  
                dic.update({i:collaborations})
                collaborations=[]
                
            return dic
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def delete_attachment(request, attachment_id):
        file = Google_Calendar_Attachments.objects.get(pk=attachment_id)
        if(CalendarHandler.google_drive_delete_file(request, file.file_id) == ""):
            file.delete()
            return True
        else:
            return False
