from system_administration.models import Graphics_Data_Access
from system_administration.render_access import Access_Render
from system_administration.system_error_handling import ErrorHandling
from datetime import datetime
import logging
import traceback

class GraphicsTeam_Render_Access:

    logger=logging.getLogger(__name__)

    def get_common_access(request):
        ''' This function checks the common access permissions for users such as administrator or coordinator. It will return True if conditions match. The method takes a REQUEST and verifies access '''
        try:
            # get the user and username. Username will work as IEEE ID and Developer username both
            user=request.user
            username=user.username
            
            # generate superuser or staff user access
            system_manager_access=False
            if(Access_Render.system_administrator_superuser_access(username=username) or Access_Render.system_administrator_staffuser_access(username=username)):
                system_manager_access=True
            
            #generate branch eb access
            branch_eb_access=False
            if(Access_Render.eb_access(username=username)):
                branch_eb_access=True
            
            # generate Faculty Advisor Access
            faculty_advisor_access=False
            if(Access_Render.faculty_advisor_access(username=username)):
                faculty_advisor_access=True
            
            # generate branch coordinator access
            branch_co_ordinator_access=False
            if(Access_Render.co_ordinator_access(username=username)):
                branch_co_ordinator_access=True
            
            # if any of this is true, grant access
            if(system_manager_access or branch_eb_access or faculty_advisor_access or branch_co_ordinator_access):
                return True
            else:
                return False
        except Exception as e:
            GraphicsTeam_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            return False
        
    def access_for_events(request):
        ''' This function checks if the requested user has access to events. Will return True if it has access permission '''
        try:
            # get the user and username. Username will work as IEEE ID and Developer username both
            user=request.user
            username=user.username

            #Get member from graphics data access table
            get_member = Graphics_Data_Access.objects.filter(ieee_id=username)
            #Check if the member exits
            if(get_member.exists()):
                #The member exists. Now check if it has events access
                if(get_member[0].event_access or GraphicsTeam_Render_Access.get_common_access(request)):
                    return True
                else:
                    return False
            else:
                #The member does not exist in the permissions table
                return False
        except Exception as e:
            if(GraphicsTeam_Render_Access.get_common_access(request)):
                return True
            else:
                GraphicsTeam_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                return False