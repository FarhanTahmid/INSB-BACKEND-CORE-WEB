from system_administration.render_access import Access_Render
from system_administration.system_error_handling import ErrorHandling
from datetime import datetime
import logging
import traceback

class SC_Ag_Render_Access:

    logger=logging.getLogger(__name__)
    
    def get_sc_ag_common_access(request,sc_ag_primary):
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
            
            # generate sc_ag_eb member access
            sc_ag_eb_member_access=False
            if(Access_Render.sc_ag_eb_access(username=username,sc_ag_primary=sc_ag_primary)):
                sc_ag_eb_member_access=True
            
            # if any of this is true, grant access
            if(system_manager_access or branch_eb_access or faculty_advisor_access or sc_ag_eb_member_access):
                return True
            else:
                return False
        except Exception as e:
            SC_Ag_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    
        
        