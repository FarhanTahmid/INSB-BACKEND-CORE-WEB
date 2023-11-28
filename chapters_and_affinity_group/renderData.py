from django.contrib import messages
from .models import SC_AG_Members
from users.models import Members
from port.models import Chapters_Society_and_Affinity_Groups,Teams,Roles_and_Position
import logging
from system_administration.system_error_handling import ErrorHandling
import traceback
from datetime import datetime

class Sc_Ag:
    logger=logging.getLogger(__name__)
        
    def add_insb_members_to_sc_ag(request,sc_ag_primary,ieee_id,team_pk,position_id):
        '''This method adds an existing Member Registered in INSB to a SC or AG'''
        try:
            if(SC_AG_Members.objects.filter(sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),member=Members.objects.get(ieee_id=ieee_id)).exists()):
                messages.info(request,"The Member already exists in Database")
            else:
                new_sc_ag_member=SC_AG_Members.objects.create(sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)
                                                            ,member=Members.objects.get(ieee_id=ieee_id))
                if team_pk is not None:
                    new_sc_ag_member.team=Teams.objects.get(pk=team_pk)
                if position_id is not None:
                    new_sc_ag_member.position=Roles_and_Position.objects.get(id=position_id)
                new_sc_ag_member.save()
                messages.success(request,f"{new_sc_ag_member.member.name} added to Members of ")
                return True
            
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        