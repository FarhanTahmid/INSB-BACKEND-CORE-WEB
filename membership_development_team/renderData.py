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
        
        '''Gets the team id from the database only for Membership Development Team. Not the right approach'''
        
        team=Teams.objects.get(team_name="Membership Development")
        return team.id
    
    def get_member_with_postion(position):
        '''Returns MDT Team Members with positions'''
        team_members=Members.objects.filter(team=MDT_DATA.get_team_id(),position=position)
        return team_members
    
    def load_team_members():
        
        '''This function loads all the team members for membership development team'''

        load_team_members=Members.objects.filter(team=MDT_DATA.get_team_id()).order_by('position')
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    
    def load_team_permissions():
        
        '''This function loads all the team permissions assigned for the team'''
        
        load_permissions_mdt=Access_Criterias.objects.filter(team=MDT_DATA.get_team_id())
        permission_criterias=[]
        for i in range(len(load_permissions_mdt)):
            permission_criterias.append(load_permissions_mdt[i])

        return permission_criterias
    
    
    def get_team_access_data():
        
        '''This function loads the access data specified for the team members only'''
        
        load_data=Access_Criterias.objects.filter(team=Teams.objects.get(id=MDT_DATA.get_team_id()))
        data=[]
        for i in range(len(load_data)):
            data.append(load_data[i])
        return data                
    
    def get_member_access_data():
        
        '''This function loads the access data specified for the particular team members'''
        
        load_data=Team_Data_Access.objects.filter(team=Teams.objects.get(id=MDT_DATA.get_team_id()))
        data=[]
        for i in range(len(load_data)):
            data.append(load_data[i])
        return data
    
    
    def mdt_access_modifications(requested_permission_list,ieee_id):
        
        '''This method sets all the access modifications for MDT TEAM Only'''
        
        #all the permissions in the MDT permission criteria updates for inividual member selected. It creates objects for the member
        #permission criteria and updates the value of access upon a click on update button in the frontEnd.
        
        
        #getting the MDT team's access criterias
        team_data=MDT_DATA.get_team_access_data()
        team_data_access=[]
        for i in range(len(team_data)):
            team_data_access.append(team_data[i].id)
        
        
        #check algorithm for reuested access list and team data access list. if item matches, we set the permission to true. If not set it to false
        
        for access in team_data_access:
            
            #check if item does or does not exist in both of the lists, do the false permission work if it is not present in the requested permission list and do the true work if its present.
            
            if access not in (team_data_access and requested_permission_list): #checking if item doesnot exist
                
                #check if the permission object already exists in the database
                
                if(Team_Data_Access.objects.filter(criteria=Access_Criterias.objects.get(id=access),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id())).exists()):
                    
                    #if permission exists update the particular permission to false as it is now not checked in the reuested permission list
                    
                    Team_Data_Access.objects.filter(criteria=Access_Criterias.objects.get(id=access),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id())).update(has_permission=False)
                   
                else:
                    
                    #if permission doesnot exists, the system creates an object of permission with that particular member and team and automatically sets that value of access to false.

                    Team_Data_Access.objects.create(criteria=Access_Criterias.objects.get(id=access),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id()),has_permission=False)

                
              
            elif access in (team_data_access and requested_permission_list): #check the permissions that exists in both of the lists 
                
                #check if the permission object already exists in the database

                if(Team_Data_Access.objects.filter(criteria=Access_Criterias.objects.get(id=access),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id())).exists()):
                    
                    #if permission exists update the particular permission to true as it is now checked in the reuested permission list
                    
                    Team_Data_Access.objects.filter(criteria=Access_Criterias.objects.get(id=access),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id())).update(has_permission=True)
                    
                else:
                    
                    #if permission doesnot exists, the system creates an object of permission with that particular member and team and automatically sets that value of access to true.

                    Team_Data_Access.objects.create(criteria=Access_Criterias.objects.get(id=access),ieee_id=Members.objects.get(ieee_id=ieee_id),team=Teams.objects.get(id=MDT_DATA.get_team_id()),has_permission=True)

                
                
            