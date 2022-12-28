from users.models import Members
from port.models import Teams
from system_administration.models import Access_Criterias,Team_Data_Access

class MDT_DATA:
    
    def get_member_data(ieee_id):
        member_data=Members.objects.get(ieee_id=ieee_id)
        return {
            'ieee_id':member_data.ieee_id,
            'name':member_data.name,
            'nsu_id':member_data.nsu_id,
            'email_ieee':member_data.email_ieee,
            'email_personal':member_data.email_personal,
            'major':member_data.major,
            'contact_no':member_data.contact_no,
            'home_address':member_data.home_address,
            'date_of_birth':member_data.date_of_birth,'gender':member_data.gender,
            'facebook_url':member_data.facebook_url,
            'team':member_data.team,
            'position':member_data.position,
            'session':member_data.session,
            'last_renewal':member_data.last_renewal,        
        }
    def get_team_id():
        team=Teams.objects.get(team_name="Membership Development")
        return team.id
    
    def load_team_members():
        
        load_team_members=Members.objects.filter(team=MDT_DATA.get_team_id()).order_by('position')
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    def load_team_permissions():
        load_permissions_mdt=Access_Criterias.objects.filter(team=MDT_DATA.get_team_id())
        permission_criterias=[]
        for i in range(len(load_permissions_mdt)):
            permission_criterias.append(load_permissions_mdt[i])

        return permission_criterias
    
    
    def get_team_access_data():
        load_data=Access_Criterias.objects.filter(team=Teams.objects.get(id=MDT_DATA.get_team_id()))
        data=[]
        for i in range(len(load_data)):
            data.append(load_data[i].id)
        return data                
    
    def get_member_access_data(ieee_id):
        load_data=Team_Data_Access.objects.filter(ieee_id=ieee_id,team=Teams.objects.get(id=MDT_DATA.get_team_id()))
        data=[]
        for i in range(len(load_data)):
            data.append(load_data[i])
        return data
    
    
    def mdt_access_modifications(requested_permission_list,ieee_id):
        team_data_access=MDT_DATA.get_team_access_data()
        
        for team_access in team_data_access:
            for access_request in requested_permission_list:
                #print(f"Team access: {team_access} and Requested Access {access_request}")
                if(team_access==access_request):
                    try:
                        Team_Data_Access.objects.get(criteria=Access_Criterias.objects.get(id=access_request),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id()))
                        Team_Data_Access.objects.filter(criteria=Access_Criterias.objects.get(id=access_request),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id())).update(has_permission=True)
                    except Team_Data_Access.DoesNotExist:
                        Team_Data_Access.objects.create(ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id()),criteria=Access_Criterias.objects.get(id=access_request),has_permission=True)
                else:
                    try:
                        Team_Data_Access.objects.get(criteria=Access_Criterias.objects.get(id=access_request),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id()))
                        Team_Data_Access.objects.filter(criteria=Access_Criterias.objects.get(id=access_request),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id())).update(has_permission=False)
                    except Team_Data_Access.DoesNotExist:
                        Team_Data_Access.objects.create(ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id()),criteria=Access_Criterias.objects.get(id=access_request),has_permission=False)
        