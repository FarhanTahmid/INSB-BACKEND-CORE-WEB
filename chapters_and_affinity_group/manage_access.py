from system_administration.render_access import Access_Render
from system_administration.models import SC_AG_Data_Access
from system_administration.system_error_handling import ErrorHandling
from .models import SC_AG_Members
from port.models import Chapters_Society_and_Affinity_Groups
from users.models import Members
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
            
            #generate sc_ag eb access
            sc_ag_eb_access=False
            if(Access_Render.sc_ag_eb_access(username=username, sc_ag_primary=sc_ag_primary)):
                sc_ag_eb_access=True
            
            # generate Faculty Advisor Access
            faculty_advisor_access=False
            if(Access_Render.faculty_advisor_access(username=username)):
                faculty_advisor_access=True
            
            # if any of this is true, grant access
            if(system_manager_access or sc_ag_eb_access or faculty_advisor_access):
                return True
            else:
                return False
        except Exception as e:
            # SC_Ag_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            return False
    
    def access_for_member_details(request,sc_ag_primary):
        try:
            # get the user and username. Username will work as IEEE ID and Developer username both
            user=request.user
            username=user.username
            # get member from SC AG Data Access Table
            get_member=SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=int(username)),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
            if(get_member.exists()):
                if((get_member[0].member_details_access) or SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                    return True
                else:
                    return False
            else:
                #The member does not exist in the permissions table
                if(SC_Ag_Render_Access.get_sc_ag_common_access(request,sc_ag_primary)):
                    return True
                else:
                    return False
        except Exception as e:
            if(SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                return True
            else:
                SC_Ag_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                # ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                return False
        
    def access_for_create_event(request,sc_ag_primary):
        try:
            # get the user and username. Username will work as IEEE ID and Developer username both
            user=request.user
            username=user.username
            # get member from SC AG Data Access Table
            get_member=SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=int(username)),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
            if(get_member.exists()):
                if((get_member[0].create_event_access) or SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                    return True
                else:
                    return False
            else:
                #The member does not exist in the permissions table
                if(SC_Ag_Render_Access.get_sc_ag_common_access(request,sc_ag_primary)):
                    return True
                else:
                    return False
        except Exception as e:
            if(SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                return True
            else:
                SC_Ag_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                # ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                return False
    
    def access_for_event_details_edit(request,sc_ag_primary):
        try:
            # get the user and username. Username will work as IEEE ID and Developer username both
            user=request.user
            username=user.username
            # get member from SC AG Data Access Table
            get_member=SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=int(username)),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
            if(get_member.exists()):
                if((get_member[0].event_details_edit_access) or SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                    return True
                else:
                    return False
            else:
                #The member does not exist in the permissions table
                if(SC_Ag_Render_Access.get_sc_ag_common_access(request,sc_ag_primary)):
                    return True
                else:
                    return False
        except Exception as e:
            if(SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                return True
            else:
                SC_Ag_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                # ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                return False
    
    def access_for_panel_edit_access(request,sc_ag_primary):
        try:
            # get the user and username. Username will work as IEEE ID and Developer username both
            user=request.user
            username=user.username
            # get member from SC AG Data Access Table
            get_member=SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=int(username)),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
            if(get_member.exists()):
                if((get_member[0].panel_edit_access) or SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                    return True
                else:
                    return False
            else:
                #The member does not exist in the permissions table
                if(SC_Ag_Render_Access.get_sc_ag_common_access(request,sc_ag_primary)):
                    return True
                else:
                    return False
        except Exception as e:
            if(SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                return True
            else:
                SC_Ag_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                # ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                return False
    
    def access_for_membership_renewal_access(request,sc_ag_primary):
        try:
            # get the user and username. Username will work as IEEE ID and Developer username both
            user=request.user
            username=user.username
            # get member from SC AG Data Access Table
            get_member=SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=int(username)),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
            if(get_member.exists()):
                if((get_member[0].membership_renewal_access) or SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                    return True
                else:
                    return False
            else:
                #The member does not exist in the permissions table
                if(SC_Ag_Render_Access.get_sc_ag_common_access(request,sc_ag_primary)):
                    return True
                else:
                    return False
        except Exception as e:
            if(SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                return True
            else:
                SC_Ag_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                # ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                return False
    
    def access_for_manage_access(request,sc_ag_primary):
        try:
            # get the user and username. Username will work as IEEE ID and Developer username both
            user=request.user
            username=user.username
            # get member from SC AG Data Access Table
            get_member=SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=int(username)),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
            if(get_member.exists()):
                if((get_member[0].manage_access) or SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                    return True
                else:
                    return False
            else:
                #The member does not exist in the permissions table
                if(SC_Ag_Render_Access.get_sc_ag_common_access(request,sc_ag_primary)):
                    return True
                else:
                    return False
        except Exception as e:
            if(SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                return True
            else:
                SC_Ag_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                # ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                return False
            
    def access_for_manage_web(request,sc_ag_primary):
        try:
            # get the user and username. Username will work as IEEE ID and Developer username both
            user=request.user
            username=user.username
            # get member from SC AG Data Access Table
            get_member=SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=int(username)),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
            if(get_member.exists()):
                if((get_member[0].manage_web_access) or SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                    return True
                else:
                    return False
            else:
                #The member does not exist in the permissions table
                if(SC_Ag_Render_Access.get_sc_ag_common_access(request,sc_ag_primary)):
                    return True
                else:
                    return False
        except Exception as e:
            if(SC_Ag_Render_Access.get_sc_ag_common_access(request=request,sc_ag_primary=sc_ag_primary)):
                return True
            else:
                SC_Ag_Render_Access.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                # ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                return False
    
    