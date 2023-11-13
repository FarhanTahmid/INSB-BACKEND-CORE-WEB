from .models import Chapters_Society_and_Affinity_Groups,Roles_and_Position,Teams,Panels
from django.contrib import messages
import sqlite3

class PortData:
    def get_positions_with_sc_ag_id(request,sc_ag_primary):
        try:
            positions=Roles_and_Position.objects.filter(role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return positions
        except:
            messages.error(request,"An internal Database error occured loading the Positions!")
            return False
    
    def get_all_executive_positions_with_sc_ag_id(request,sc_ag_primary):
        try:
            executive_positions=Roles_and_Position.objects.filter(is_eb_member=True,role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return executive_positions
        except:
            messages.error(request,"An internal Database error occured loading the Positions for Executive Members!")
            return False
    
    def get_all_officer_positions_with_sc_ag_id(request,sc_ag_primary):
        try:
            officer_positions=Roles_and_Position.objects.filter(is_officer=True,role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return officer_positions
        except:
            messages.error(request,"An internal Database error occured loading the Positions for Officer Members!")
            return False
    
    def get_all_volunteer_position_with_sc_ag_id(request,sc_ag_primary):
        try:
            volunteer_positions=Roles_and_Position.objects.filter(is_officer=False,is_eb_member=False,is_sc_ag_eb_member=False,is_co_ordinator=False,is_faculty=False,role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return volunteer_positions
        except:
            messages.error(request,"An internal Database error occured loading the Positions for Volunteer Members!")
            return False
        
    def get_teams_of_sc_ag_with_id(request,sc_ag_primary):
        try:
            teams=Teams.objects.filter(team_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return teams
        except:
            messages.error(request,"An internal Database error occured loading the Positions for Executive Members!")
            return False
    
    def get_current_panel():
        '''Returns the id of the current panel of IEEE NSU SB'''
        try:            
            current_panel=Panels.objects.get(current=True)
            return current_panel.pk
        except sqlite3.OperationalError:
            return False
        except:
            return False