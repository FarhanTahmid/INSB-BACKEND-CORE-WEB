import logging
from port.models import Panels,Teams,Chapters_Society_and_Affinity_Groups,Roles_and_Position
from users.models import Panel_Members
from .models import SC_AG_Members
from datetime import datetime
from system_administration.system_error_handling import ErrorHandling
import traceback
from django.contrib import messages
from django.http import Http404

class SC_AG_Info:
    
    logger=logging.getLogger(__name__)
    
    def get_sc_ag_details(request,sc_ag_primary):
        '''This returns the SC_AG details as an object'''
        try:
            return Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404
    
    def get_sc_ag_members(request,sc_ag_primary):
        '''This returns the members of the sc_ag as a query set.'''
        try:
            return SC_AG_Members.objects.filter(sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404
    
    def get_panels_of_sc_ag(request,sc_ag_primary):
        try:
            return Panels.objects.filter(panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).order_by('-current','-year')
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404
    
    def get_teams_of_sc_ag(request,sc_ag_primary):
        '''Gets all the teams of SC AG'''
        '''Gets all the executive positions for SC AG'''
        try:
            return Teams.objects.filter(team_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404
       
    def get_sc_ag_executive_positions(request,sc_ag_primary):
        '''Gets all the executive positions for SC AG'''
        try:
            return Roles_and_Position.objects.filter(role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),is_eb_member=True)
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404
    
    def get_sc_ag_officer_positions(request,sc_ag_primary):
        '''Gets all the officer positions for SC AG'''

        try:
            return Roles_and_Position.objects.filter(role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),is_officer=True)
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404
    
    
    def get_sc_ag_executives_from_panels(request,panel_id):
        '''Gets all the executives of the panel'''
        try:    
            get_panel_members=Panel_Members.objects.filter(
                tenure=Panels.objects.get(id=panel_id),
            )
            sc_ag_eb_members=[]
            for i in get_panel_members:
                if i.position.is_sc_ag_eb_member:
                    sc_ag_eb_members.append(i)
            return sc_ag_eb_members
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404
        
    def get_sc_ag_officers_from_panels(request,panel_id):
        '''Gets all the officers of the panel'''
        try:
            get_panel_members=Panel_Members.objects.filter(
                tenure=Panels.objects.get(id=panel_id),
            )
            sc_ag_officer_members=[]
            for i in get_panel_members:
                if i.position.is_officer:
                    sc_ag_officer_members.append(i)
            return sc_ag_officer_members
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404
    
    def get_sc_ag_volunteer_from_panels(request,panel_id):
        '''Gets all the volunteers of the panel'''
        try:
            get_panel_members=Panel_Members.objects.filter(
                tenure=Panels.objects.get(id=panel_id),
            )
            sc_ag_volunteer_members=[]
            for i in get_panel_members:
                if(not i.position.is_eb_member and not i.position.is_sc_ag_eb_member and not i.position.is_co_ordinator and not i.position.is_officer and not i.position.is_faculty and not i.position.is_mentor):
                    sc_ag_volunteer_members.append(i)
            return sc_ag_volunteer_members
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404