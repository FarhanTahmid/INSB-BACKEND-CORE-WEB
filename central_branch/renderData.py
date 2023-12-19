from django.http import Http404
from port.models import Teams,Roles_and_Position,Chapters_Society_and_Affinity_Groups,Panels
from users.models import Members,Panel_Members,Alumni_Members
from django.db import DatabaseError
from system_administration.models import MDT_Data_Access
from central_events.models import SuperEvents,Events,InterBranchCollaborations,IntraBranchCollaborations,Event_Venue,Event_Permission,Event_Category
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


class Branch:

    logger=logging.getLogger(__name__)
    
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
            event_type_lower = event_type.lower()
            try:
                registered_event_category = Event_Category.objects.get(event_category = event_type_lower,event_category_for=Chapters_Society_and_Affinity_Groups.objects.get(primary = group_number))
                registered_event_category = registered_event_category.event_category.lower()
                if event_type_lower == registered_event_category:
                    return False 
            except:
                new_event_type = Event_Category.objects.create(event_category=event_type_lower,event_category_for = Chapters_Society_and_Affinity_Groups.objects.get(primary = group_number))
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
            teams=Teams.objects.all().values('primary','team_name') #returns a list of dictionaryies with the id and team name
            return teams
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Can not return all teams. Something went wrong!")
            return False
    
    def load_team_members(team_primary):
        '''This function loads all the team members from the database and also checks if the member is included in the current panel'''
        team=Teams.objects.get(primary=team_primary)
        team_id=team.id
        get_users=Members.objects.order_by('position').filter(team=team_id)
        get_current_panel=Branch.load_current_panel()
        team_members=[]
        if(get_current_panel is not None):
            for i in get_users:
                if(Panel_Members.objects.filter(member=i.ieee_id,tenure=get_current_panel.pk).exists()):
                    team_members.append(i)

        return team_members
    
    def register_super_events(super_event_name,super_event_description,start_date,end_date):
        
        '''This function registers the super event'''

        try:
            if end_date=='':
                saving_data = SuperEvents(super_event_name=super_event_name,super_event_description=super_event_description,start_date=start_date)
                saving_data.save()
            else:
                saving_data = SuperEvents(super_event_name=super_event_name,super_event_description=super_event_description,start_date=start_date,end_date=end_date)
                saving_data.save()
        except Exception as e:
            Branch.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error("Can not register super event in database. Something went wrong!")
            return False
    
    def register_event_page1(super_event_id,event_name,event_type_list,event_description,event_date,event_organiser=None):
            '''This method creates an event and registers data which are provided in event page1. Returns the id of the event if the method can create a new event successfully
            TAKES SUPER EVENT NAME, EVENT NAME, EVENT DESCRIPTION AS STRING. TAKES PROBABLE & FINAL DATE ALSO AS INPUT'''
            if event_organiser==None:
                event_organiser = 1

            if(super_event_id=="null"):
                    
                    #now create the event as super event is null
                    if(event_date==''):
                        
                        try:
                            #create event without final date included
                            new_event=Events.objects.create(
                            event_name=event_name,
                            event_description=event_description,
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
                            event_date=event_date,
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
                    
                    if(event_date==''):
                        
                        try:
                            get_super_event_id = SuperEvents.objects.get(id = super_event_id)
                            print(get_super_event_id.super_event_name)
                            new_event=Events.objects.create(
                            super_event_id=get_super_event_id,
                            event_name=event_name,
                            event_description=event_description,
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
                            print(get_super_event_id.super_event_name)
                            new_event=Events(
                            super_event_id=get_super_event_id,
                            event_name=event_name,
                            event_description=event_description,
                            event_date=event_date,
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
            event_organiser = Events.objects.get(pk = event_id).event_organiser
            group_primary = Chapters_Society_and_Affinity_Groups.objects.get(primary = str(event_organiser)).primary
            print(group_primary)
            print(inter_branch_collaboration_list)
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

    def update_event_details(event_id, event_name, event_description, super_event_id, event_type_list,publish_event, event_date, inter_branch_collaboration_list, intra_branch_collaboration, venue_list_for_event,
                             flagship_event,registration_fee,registration_fee_amount,form_link):
        ''' Update event details and save to database '''

        try:
            #Get the selected event details from database
            event = Events.objects.get(pk=event_id)

            #Check if super id is null
            if(super_event_id == 'null'):

                #Check if date is empty
                if(event_date == ""):
                    #Update without date and super id
                    event.event_name = event_name
                    event.event_description = event_description
                else:
                    #Update without super id
                    event.event_name = event_name
                    event.event_description = event_description
                    event.event_date = event_date
            else:
                ''' Super ID is not null '''

                #Check if date is empty
                if(event_date == ""):
                    #Update without date
                    event.event_name = event_name
                    event.event_description = event_description
                    event.super_event_id = SuperEvents.objects.get(id=super_event_id)
                else:
                    #Update all
                    event.event_name = event_name
                    event.event_description = event_description
                    event.super_event_id = SuperEvents.objects.get(id=super_event_id)
                    event.event_date = event_date
                    
            #Clear event type
            event.event_type.clear()
            #Add the event types from event_type_list
            event.event_type.add(*event_type_list)
            event.publish_in_main_web = publish_event
            event.flagship_event = flagship_event
            event.registration_fee = registration_fee
            event.registration_fee_amount = registration_fee_amount
            event.form_link = form_link
            event.save()
            event_venue = Event_Venue.objects.filter(event_id = event_id)
            for venues in event_venue:
                venues.delete()
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

            return True
        except:
            return False

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
            get_panel_members=Panel_Members.objects.filter(tenure=panel_id).all().order_by('position')
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
        return Events.objects.all().order_by('-event_date')
    
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
        
    def load_event_published(event_id):
        '''This function will return wheather the event is published or not'''

        return Events.objects.get(id = event_id).publish_in_main_web
    
    def is_flagship_event(event_id):

        '''This function will return wheather the event is flagship or not'''

        return Events.objects.get(id = event_id).flagship_event
    
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
        return SuperEvents.objects.all()
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
        return events_with_collaborated_events.order_by('-event_date')
        
    
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
        
        return Events.objects.filter(event_organiser=5).order_by('-event_date')
    

    def delete_event(event_id):
        ''' This function deletes event from database '''
        try:
            #Match event id and delete that event
            Events.objects.get(id = event_id).delete()
            return True
        except:
            return False