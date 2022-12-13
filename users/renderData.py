from users.models import Members
from port.models import Roles_and_Position,Teams
class LoggedinUser:
    
    def __init__(self,user):
        self.user=user
    
    def getUserData(self):
        ieee_id=self.user.username
        try:
            get_Member_details=Members.objects.get(ieee_id=ieee_id)
            
        except Members.DoesNotExist:
            return False
        return {
            'name':get_Member_details.name,
            'position':get_Member_details.position,
            'team':get_Member_details.team,
            'ieee_id':get_Member_details.ieee_id,
            'email':get_Member_details.email_ieee,
            'nsu_id':get_Member_details.nsu_id,
        }