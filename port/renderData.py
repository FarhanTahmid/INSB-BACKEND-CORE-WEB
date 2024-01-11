from .models import Chapters_Society_and_Affinity_Groups,Roles_and_Position,Teams,Panels
from django.contrib import messages
from users.models import Panel_Members
from datetime import datetime
import sqlite3
import logging
import traceback
from system_administration.system_error_handling import ErrorHandling

class PortData:
    logger=logging.getLogger(__name__)
    
    def get_sc_ag(request,primary):
        '''Returns the details of the SC AG'''
        try:
            return Chapters_Society_and_Affinity_Groups.objects.get(primary=primary)
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.info(request,'Something went wrong fetching the Chapter and Affinity Group')
            return False
    
    def get_all_sc_ag(request):
        '''Returns all the Chapters, Affinity Groups with their Primary. Branch is excluded.'''
        try:
            return Chapters_Society_and_Affinity_Groups.objects.all().exclude(primary=1).order_by('primary') #excluding branch's Primary
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.info(request,'Something went wrong fetching the Chapters and Affinity Groups')
            return False
        
    def get_positions_with_sc_ag_id(request,sc_ag_primary):
        try:
            positions=Roles_and_Position.objects.filter(role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id','is_faculty','is_eb_member','is_sc_ag_eb_member','is_co_ordinator','is_officer')
            return positions
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"An internal Database error occured loading the Positions!")
            return False
    
    def get_branch_ex_com_from_sc_ag(request):
        '''This method gets all the Chairs of SC AG from current panel'''
        try:
            chairs_of_sc_ag=[]
            # as sc_ag_primary extends from 2-5, if in future any sc ag extends, extend the range
            for i in range(2,6):
                try:
                    get_current_panel_of_sc_ag=Panels.objects.get(current=True,panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=i))
                except:
                    continue
                get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=get_current_panel_of_sc_ag.pk))
                if(get_panel_members.exists()):
                    for member in get_panel_members:
                        if(member.position.is_sc_ag_eb_member):
                            if(member.position.role=="Chair"):
                                chairs_of_sc_ag.append(member)
            return chairs_of_sc_ag
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"An internal Database error occured loading the Excom!")
    
    def get_sc_ag_faculty_members(request):
        '''This function returns all the faculties related to sc ag'''
        try:
            faculties_of_sc_ag=[]
            for i in range(2,6):
                try:
                    get_current_panel_of_sc_ag=Panels.objects.get(current=True,panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=i))
                except:
                    continue
                get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=get_current_panel_of_sc_ag.pk))
                if(get_panel_members.exists()):
                    for member in get_panel_members:
                        if(member.position.is_sc_ag_eb_member and member.position.is_faculty):
                            faculties_of_sc_ag.append(member)
            return faculties_of_sc_ag
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"An internal Database error occured loading the Faculties of SC AG!")

    def get_branch_ex_com_from_sc_ag_by_year(request,panel_year):
        '''This methods loads SC AG Chairs by year'''
        try:
            chairs_of_sc_ag=[]
            for i in range(2,6):
                try:
                    get_panel_of_sc_ag=Panels.objects.get(year=panel_year,panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=i))
                except:
                    continue
                get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=get_panel_of_sc_ag.pk))
                if(get_panel_members.exists()):
                    for member in get_panel_members:
                        if(member.position.is_sc_ag_eb_member):
                            if(member.position.role=="Chair"):
                                chairs_of_sc_ag.append(member)
            return chairs_of_sc_ag
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"An internal Database error occured loading the Excom!")
                
    def get_all_executive_positions_of_branch(request,sc_ag_primary):
         
        try:
            executive_positions=Roles_and_Position.objects.filter(is_eb_member=True,role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return executive_positions
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"An internal Database error occured loading the Positions for Executive Members!")
            return False
    
    def get_all_officer_positions_with_sc_ag_id(request,sc_ag_primary):
        try:
            officer_positions=Roles_and_Position.objects.filter(is_officer=True,role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return officer_positions
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"An internal Database error occured loading the Positions for Officer Members!")
            return False
    
    def get_all_volunteer_position_with_sc_ag_id(request,sc_ag_primary):
        try:
            volunteer_positions=Roles_and_Position.objects.filter(is_officer=False,is_eb_member=False,is_sc_ag_eb_member=False,is_co_ordinator=False,is_faculty=False,role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return volunteer_positions
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"An internal Database error occured loading the Positions for Volunteer Members!")
            return False
        
    def get_teams_of_sc_ag_with_id(request,sc_ag_primary):
        '''Returns the Active teams of all Branch+Sc AG'''
        try:

            teams=Teams.objects.filter(is_active=True,team_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return teams
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"An internal Database error occured loading the Positions for Executive Members!")
            return False
    
    def get_team_details(request,team_primary):
        '''Returns the object of team'''
        
        try:
            team_details=Teams.objects.get(primary=team_primary)
            return team_details
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"An internal Database error occured loading the Team Details!")
            return False
    
    def get_current_panel():
        '''Returns the id of the current panel of IEEE NSU SB'''
        try:            
            current_panel=Panels.objects.get(current=True,panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=1))
            return current_panel.pk
        except Panels.DoesNotExist:
            return False
        except sqlite3.OperationalError:
            return False
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def get_specific_team_members_of_current_panel(request,team_primary):
        try:
            current_panel=PortData.get_current_panel()
            if(current_panel):
                get_current_panel_members=Panel_Members.objects.filter(
                    tenure=Panels.objects.get(pk=current_panel),
                    team=Teams.objects.get(primary=team_primary)
                )
                return get_current_panel_members
            else:
                messages.info("There is no current panel available to load the teams!")
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    def create_positions(request,sc_ag_primary,role,is_eb_member,is_sc_ag_eb_member,is_officer,is_co_ordinator,is_faculty,is_mentor):
        '''Creates Positions in the Roles and Positions Table with Different attributes for sc ag and branch as well'''
        try:
            # get the last object of the model
            get_the_last_object=Roles_and_Position.objects.all().last()
            # The logic of creating new position is to assign the id = las objects id + 1.
            # this ensures that ids never conflict with each other
            new_position=Roles_and_Position.objects.create(
                id=get_the_last_object.id + 1,
                role=role,role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),
                is_eb_member=is_eb_member,is_sc_ag_eb_member=is_sc_ag_eb_member,
                is_officer=is_officer,is_co_ordinator=is_co_ordinator,is_faculty=is_faculty,is_mentor=is_mentor
            )
            new_position.save()
            messages.success(request,f"New Position: {role} was created!")
            return True
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def create_team(request,sc_ag_primary,team_name):
        '''Creates a Team with given name for sc ag and branch'''
        try:    
            get_the_last_team_primary=Teams.objects.all().order_by('-primary').first()
            # The logic of creating new Team is to assign the primary = last objects primary + 1.
            # this ensures that primary of teams never conflict with each other
            new_team=Teams.objects.create(
                team_name=team_name,
                primary=get_the_last_team_primary.primary + 1,
                team_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)
            )
            messages.success(request,f"A new team : {new_team.team_name} was created!")
            new_team.save()
            return True
        except Exception as e:
            PortData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Error Creating Team. Something went wrong!")
            return False