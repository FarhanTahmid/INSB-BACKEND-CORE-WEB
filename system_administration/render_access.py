from port.models import Roles_and_Position,Teams
from users.models import Members
from django.contrib.auth .models import User
class Access_Render:
    def faculty_advisor_access(username):
        try:
            get_faculty=Members.objects.get(ieee_id=int(username))
            if(get_faculty.position.id==14):
                return True
            else:
                False
        except Members.DoesNotExist:
            return False
        except:
            return False
    def eb_access(username):
        try:
            get_eb=Members.objects.get(ieee_id=int(username))
            if(get_eb.position.id<=8):
                return True
            else:
                False
        except Members.DoesNotExist:
            return False
        except:
            return False
    def co_ordinator_access(username):
        
        try:
            get_co_ordinator=Members.objects.get(ieee_id=int(username))
            
            if(get_co_ordinator.position.id==9):
                return True
            else:
                return False
        except Members.DoesNotExist:
            return False
        except:
            return False
    def team_co_ordinator_access(team_id,username):
        try:
            get_co_ordinator=Members.objects.get(ieee_id=int(username))
            
            if(get_co_ordinator.position.id==9 and (get_co_ordinator.team.id==team_id)):
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