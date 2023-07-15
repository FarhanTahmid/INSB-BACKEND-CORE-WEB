from port.models import Teams,Roles_and_Position,Chapters_Society_and_Affinity_Groups
from users.models import Members
from django.db import DatabaseError
from system_administration.models import MDT_Data_Access
from . models import SuperEvents,Events,InterBranchCollaborations,IntraBranchCollaborations,Event_Venue,Event_Permission,Event_type
from events_and_management_team.models import Venue_List, Permission_criteria
from system_administration.render_access import Access_Render





class Branch:
    
    def load_teams():
        
        '''This function returns all the teams in the database'''
        
        teams=Teams.objects.all().values('id','team_name') #returns a list of dictionaryies with the id and team name
        return teams
    
    def load_team_members(team_id):
        
        '''This function loads all the team members from the database'''

        team_members=Members.objects.order_by('position').filter(team=team_id)
        return team_members
    def load_roles_and_positions():
        positions=Roles_and_Position.objects.all().order_by('-id')
        return positions
    def load_all_insb_members():
        insb_members=Members.objects.all().order_by('nsu_id')
        return insb_members
    def add_member_to_team(ieee_id,team,position):
        '''This function adds member to the team'''
        
        try:
            if(team=="12"): #Checking if the team is MDT as its id is 12
                
                Members.objects.filter(ieee_id=ieee_id).update(team=team,position=position)
                
                data_access_instance=MDT_Data_Access(ieee_id=Members.objects.get(ieee_id=ieee_id),
                                                     renewal_data_access=False,
                                                     insb_member_details=False,
                                                     recruitment_session=False,
                                                     recruited_member_details=False) #create data access for the member with default value set to false
                
                data_access_instance.save()
                return True
            else:
                
                Members.objects.filter(ieee_id=ieee_id).update(team=team,position=position)
                return True
        except Members.DoesNotExist:
            return False
        except:
            return DatabaseError
    
    def load_all_events():
        return Events.objects.all()
    def load_all_mother_events():
        '''This method loads all the mother/Super events'''
        return SuperEvents.objects.all()
    def load_all_inter_branch_collaboration_options():
        '''This loads all the chapters and Societies of the branch'''
        return Chapters_Society_and_Affinity_Groups.objects.all()
    
    def load_all_event_type():
        return Event_type.objects.all()
    
    def register_event_page1(super_event_name,event_name,event_description,probable_date,final_date):
        '''This method creates an event and registers data which are provided in event page1. Returns the id of the event if the method can create a new event successfully
        TAKES SUPER EVENT NAME, EVENT NAME, EVENT DESCRIPTION AS STRING. TAKES PROBABLE & FINAL DATE ALSO AS INPUT'''
        
        if(super_event_name=="null"):
                
                #now create the event as super event is null
                if(final_date==''):
                    
                    try:
                        #create event without final date included
                        new_event=Events(
                        event_name=event_name,
                        event_description=event_description,
                        probable_date=probable_date
                        )
                        new_event.save()
                        
                        return new_event.id
                    except:
                        return False #general error
                else:
                    try:
                        #create event with final date included
                        new_event=Events(
                        event_name=event_name,
                        event_description=event_description,
                        probable_date=probable_date,
                        final_date=final_date
                        )
                        new_event.save()
                        return new_event.id
                    except:
                        return False #general error    
        else:
                 #now create the event under super event in the event models
                
                if(final_date==''):
                    
                    try:
                        get_super_event_id = SuperEvents.objects.get(id = super_event_name)
                        new_event=Events(
                        super_event_name=get_super_event_id,
                        event_name=event_name,
                        event_description=event_description,
                        probable_date=probable_date
                        )
                        new_event.save()
                        return new_event.id
                    except:
                        return False #general Error
                else:
                    try:
                        get_super_event_id = SuperEvents.objects.get(id = super_event_name)
                        print(get_super_event_id.super_event_name)
                        new_event=Events(
                        super_event_name=get_super_event_id,
                        event_name=event_name,
                        event_description=event_description,
                        probable_date=probable_date,
                        final_date=final_date
                        )
                        new_event.save()
                        return new_event.id
                    except:
                        return False
    
    def register_event_page2(inter_branch_collaboration_list,intra_branch_collaboration,event_id):
        
            '''This method creates collaborations related to the events and registers data which are provided in event page2
            TAKES INTER BRANCH COLLABORATION LIST, INTRA BRANCH COLLABORATION STRING AND EVENT ID AS PARAMETER'''

        
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
                    new_event_intra_branch_collaboration.save()
                    return True #intra branch collab created, now go to third page
                
                
            #now checking for the criterias where there are inter branch collaboration
            else:
                #checking if the intra branch collab option is still null. If null, only register for intra branch collaboration
                if(intra_branch_collaboration==""):
                    for id in inter_branch_collaboration_list:
                        
                            #check for existing events with the same inter branch collab
                            check_for_existing_events=InterBranchCollaborations.objects.filter(event_id=event_id,collaboration_with=id)
                            if(check_for_existing_events.exists()):
                                check_for_existing_events.update(collaboration_with=id) #this piece of code is really not needed just used to avoid errors and usage of extra memory
                            else:
                            #if there is no previous record of this event with particular collab option, register a new one
                                new_event_inter_branch_collaboration=InterBranchCollaborations(
                                    event_id=Events.objects.get(id=event_id),
                                    collaboration_with=Chapters_Society_and_Affinity_Groups.objects.get(id=id)
                                )   
                                new_event_inter_branch_collaboration.save()
                                return True
                        
                #now register for the both collaboration option when both are filled
                else:
                    #firstly for inter branch collaboration option, register for events as usual
                    for id in inter_branch_collaboration_list:
                        
                            #check for existing events with the same inter branch collab
                            check_for_existing_events=InterBranchCollaborations.objects.filter(event_id=event_id,collaboration_with=id)
                            if(check_for_existing_events.exists()):
                                check_for_existing_events.update(collaboration_with=id) #this piece of code is really not needed just used to avoid errors and usage of extra memory
                            else:
                            #if there is no previous record of this event with particular collab option, register a new one
                                new_event_inter_branch_collaboration=InterBranchCollaborations(
                                    event_id=Events.objects.get(id=event_id),
                                    collaboration_with=Chapters_Society_and_Affinity_Groups.objects.get(id=id) 
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
    
    def event_page_access(user):

        '''function for acceessing particular memebers into event page through
        portal'''

        try:
            user_id = user.username
            member = Members.objects.get(ieee_id=int(user_id))
            roles_and_positions = Roles_and_Position.objects.get(id = member.position.id)
            if roles_and_positions.panel_member:
                return True
            else:
                return False
        except:
            
            '''Super users and staff users can access'''

            has_access= Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username)
            return has_access
        
            
        