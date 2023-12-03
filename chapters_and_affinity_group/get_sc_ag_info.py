import logging
from port.models import Panels,Chapters_Society_and_Affinity_Groups,Roles_and_Position
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
        
    def get_sc_ag_executive_positions(request,sc_ag_primary):
        try:
            return Roles_and_Position.objects.filter(role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),is_eb_member=True)
        except Exception as e:
            SC_AG_Info.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return Http404
    
    def get_sc_ag_executives_from_panels(request,sc_ag_primary,panel_id):
        get_panel_members=Panel_Members.objects.filter(
            tenure=Panels.objects.get(id=panel_id),
        )
        sc_ag_eb_members=[]
        for i in get_panel_members:
            if i.position.is_eb_member:
                sc_ag_eb_members.append(i)
        return sc_ag_eb_members
        