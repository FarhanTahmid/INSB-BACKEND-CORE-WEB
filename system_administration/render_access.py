from port.models import Roles_and_Position,Teams
from users.models import Members,Panel_Members
from django.contrib.auth .models import User
from port.renderData import PortData
class Access_Render:

    '''
    The main theory of access render is to control views for different users
    To control the access of Faculty,EB,officers, the algorithm is
        -check if the member exists in the current running panel set by the system
        -check their positions and cross match if they are EB,co-ordinators or faculty
        -if and only if everything checks up, we return True for access, otherwise its always False.
    '''
    
    def is_panel_member(username):
        '''This fucntion checks if a member belongs to the current panel of INSB'''
        # get panel id, this is only for branch panels
        get_current_panel_id=PortData.get_current_panel()
        # check if member exists
        if(Panel_Members.objects.filter(tenure=get_current_panel_id,member=username).exists()):
            return True
        else:
            return False
        
    def faculty_advisor_access(username):
        try:
            if(Access_Render.is_panel_member(username=username)):
                get_faculty=Members.objects.get(ieee_id=int(username))
                if(get_faculty.position.is_faculty):
                    return True
                else:
                    return False
            else:
                return False
        except Members.DoesNotExist:
            return False
        except:
            return False
        
    def eb_access(username):
        try:
            
            # if member is present in the current panel
            if(Access_Render.is_panel_member(username=username)):
                get_eb=Members.objects.get(ieee_id=int(username))
                if(get_eb.position.is_eb_member):
                    return True
                else:
                    False
            else:
                return False
            
        except Members.DoesNotExist:
            return False
        except:
            return False
    def co_ordinator_access(username):
        
        try:
            # first get if the member exists in the current panel
            if(Access_Render.is_panel_member(username=username)):                # if member is present in the current panel
                get_co_ordinator=Members.objects.get(ieee_id=int(username))
                if(get_co_ordinator.position.is_officer) and (get_co_ordinator.position.is_co_ordinator):
                    return True
                else:
                    return False
            else:
                return False
        except Members.DoesNotExist:
            return False
        except:
            return False
    def team_co_ordinator_access(team_id,username):
        try:
            if (Access_Render.is_panel_member(username=username)):
                get_co_ordinator=Members.objects.get(ieee_id=int(username))
                
                if(get_co_ordinator.position.is_officer and (get_co_ordinator.position.is_co_ordinator) and (get_co_ordinator.team.id==team_id)):
                    return True
                else:
                    return False
        except Members.DoesNotExist:
            return False
        except:
            return False
    
    def officer_access(username):
        try:
            if(Access_Render.is_panel_member(username=username)):
                get_officer=Members.objects.get(ieee_id=int(username))
                if(get_officer.position.is_officer):
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False
    
    def team_officer_access(team_id,username):
        try:
            if (Access_Render.is_panel_member(username=username)):
                get_officer=Members.objects.get(ieee_id=int(username))
                
                if(get_officer.position.is_officer and (get_officer.team.id==team_id)):
                    return True
                else:
                    return False
        except Members.DoesNotExist:
            return False
        except:
            return False
        
    def system_administrator_superuser_access(username):
        try:
            access=User.objects.get(username=username)
            if(access.is_superuser):
                return True
            else:
                return False
        except:
            return False
    def system_administrator_staffuser_access(username):
        try:
            access=User.objects.get(username=username)
            if(access.is_staff()):
                return True
            else:
                return False
        except:
            return False