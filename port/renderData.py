from .models import Chapters_Society_and_Affinity_Groups,Roles_and_Position
from django.contrib import messages

class PortData:
    def get_positions_with_sc_ag_id(request,sc_ag_primary):
        try:
            positions=Roles_and_Position.objects.filter(role_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).all().order_by('id')
            return positions
        except:
            messages.error(request,"An internal Database error occured loading the Positions for Executive Members!")
            return False