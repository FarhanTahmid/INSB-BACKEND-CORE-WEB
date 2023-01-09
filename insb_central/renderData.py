from port.models import Teams,Roles_and_Position
from users.models import Members
from django.db import DatabaseError
from system_administration.models import MDT_Data_Access


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
                data_access_instance=MDT_Data_Access(ieee_id=ieee_id,
                                                     renewal_data_access=False,
                                                     insb_member_details=False,
                                                     recruitment_session=False,
                                                     recruited_member_details=False) #create data access for the member with default value set to false
                data_access_instance.save()
                return True
            else:
                print("Inside False loop")
                Members.objects.filter(ieee_id=ieee_id).update(team=team,position=position)
                return True
        except Members.DoesNotExist:
            return False
        except:
            return DatabaseError