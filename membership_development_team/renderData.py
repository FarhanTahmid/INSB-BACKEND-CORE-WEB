from . models import Renewal_Form_Info,Renewal_Sessions
from membership_development_team.models import Renewal_requests
from users.models import Members
from port.models import Teams,Roles_and_Position
from system_administration.models import MDT_Data_Access
from system_administration.render_access import Access_Render
from datetime import date
from datetime import datetime

class MDT_DATA:
    
    def get_member_data(ieee_id):
        '''Returning INSB MEMBERS DATA'''
        return Members.objects.get(ieee_id=ieee_id)
    
    def get_member_account_status(ieee_id):

        try:
            today=date.today()
            
            get_member=Members.objects.get(ieee_id=ieee_id)
            get_last_renewal_session=get_member.last_renewal_session
            
            #the logic here is to find the last renewal session of the Member
            #so first we check if the member has a last renewal session.
            # if the last renewal session is none, we then check the recruitment session of the user.
            #we then compare the time of today and time of recruitment/renewal session with a time span of 365 days(As ieee membership is of 1 year)
             
            if(get_last_renewal_session is None):
                #if renewal session is none get the recruitment session
                get_recruitment_session=get_member.session
                #getting the difference of time of today and recruitment session time
                difference_of_time=(datetime.strptime(str(today), "%Y-%m-%d") - datetime.strptime(str((get_recruitment_session.session_time)), "%Y-%m-%d")).days
                
                if(difference_of_time<365):
                    #returning true if the difference of time is less than 365 days (1 year)
                    return True
                elif(difference_of_time>365):
                    #returning false if difference of time is grater than 365 days (1year)
                    return False  

            else:
                #if renewal session exists we only compare present date and last renewal session date and nothing else
                difference_of_time=(datetime.strptime(str(today), "%Y-%m-%d") - datetime.strptime(str(get_last_renewal_session.session_time), "%Y-%m-%d")).days
                
                if(difference_of_time<365):
                    #returning true if the difference of time is less than 365 days (1 year)
                    return True
                elif(difference_of_time>365):
                    #returning false if difference of time is grater than 365 days (1year)
                    return False 
                
        except:
            #now for some member the status would be unknown if both recruitment session and renewal session is not available. for this reason we  return a False Status
            return False
            
    def get_team_id():
        
        '''Gets the team id from the database only for Membership Development Team. Not the right approach'''
        
        team=Teams.objects.get(primary=7)
        
        return team.id
    
    def get_member_with_postion(position):
        '''Returns MDT Team Members with positions'''
        team_members=Members.objects.filter(team=MDT_DATA.get_team_id(),position=position)
        return team_members
    
    
    def getRenewalInvoiceQuantity(request_id,info):
        getData=Renewal_requests.objects.get(id=request_id)
        if(info=='ieee'):
            if getData.ieee_renewal_check:
                return 1
            else:
                return 0
        if(info=='pes'):
            if getData.pes_renewal_check:
                return 1
            else:
                return 0
        if(info=='ras'):
            if getData.ras_renewal_check:
                return 1
            else:
                return 0
        if(info=='ias'):
            if getData.ias_renewal_check:
                return 1
            else:
                return 0
            
        if(info=='wie'):
            if getData.wie_renewal_check    :
                return 1
            else:
                return 0
    
    def getPaymentAmount(request_id,info,form_id):
        getData=Renewal_requests.objects.get(id=request_id)
        form_credentials=Renewal_Form_Info.objects.get(form_id=form_id)

        if(info=='ieee'):
            if getData.ieee_renewal_check:
                return int(form_credentials.ieee_membership_amount)
            else:
                return 0
        if(info=='pes'):
            if getData.pes_renewal_check:
                return int(form_credentials.ieee_pes_membership_amount)
            else:
                return 0
        if(info=='ras'):
            if getData.ras_renewal_check:
                return int(form_credentials.ieee_ras_membership_amount)
            else:
                return 0
        if(info=='ias'):
            if getData.ias_renewal_check:
                return int(form_credentials.ieee_ias_membership_amount)
            else:
                return 0
            
        if(info=='wie'):
            if getData.wie_renewal_check:
                return int(form_credentials.ieee_wie_membership_amount)
            else:
                return 0
    
    def load_team_members():
        
        '''This function loads all the team members for membership development team'''

        load_team_members=Members.objects.filter(team=MDT_DATA.get_team_id()).order_by('position')
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    
    
    
    def load_mdt_data_access():
        return MDT_Data_Access.objects.all()
    
    
    def mdt_access_modifications(insb_member_details_permission,recruitment_session_permission,
            recruited_member_details_permission,
            renewal_data_access_permission,ieee_id):
        try:
            MDT_Data_Access.objects.filter(ieee_id=ieee_id).update(insb_member_details=insb_member_details_permission,
                                       recruited_member_details=recruited_member_details_permission,
                                       recruitment_session=recruitment_session_permission,renewal_data_access=renewal_data_access_permission)
            return True
        except MDT_Data_Access.DoesNotExist:
            return False

    
    def insb_member_details_view_control(username):
        '''in here all the username = ieee_id '''
        faculty_advisor_access=Access_Render.faculty_advisor_access(username=username)
        eb_access=Access_Render.eb_access(username=username)
        team_co_ordinator_access=Access_Render.team_co_ordinator_access(team_id=MDT_DATA.get_team_id(),username=username)
        custom_data_access=False
        try:
            try:
                c=MDT_Data_Access.objects.get(ieee_id=int(username))
                if(c.insb_member_details):
                    custom_data_access=True        
                else:
                    custom_data_access=False
            except MDT_Data_Access.DoesNotExist:
                custom_data_access=False
        except:
            custom_data_access=False
        
        if(faculty_advisor_access):
            return True
        elif(eb_access):
            return True
        elif(team_co_ordinator_access):
            return True
        elif(custom_data_access):
            return True
        else:
            return False
        
    def renewal_data_access_view_control(username):
        '''in here all the username = ieee_id '''
        faculty_advisor_access=Access_Render.faculty_advisor_access(username=username)
        eb_access=Access_Render.eb_access(username=username)
        team_co_ordinator_access=Access_Render.team_co_ordinator_access(team_id=MDT_DATA.get_team_id(),username=username)
        custom_data_access=False
        try:
            try:
                c=MDT_Data_Access.objects.get(ieee_id=int(username))
                if(c.renewal_data_access):
                    custom_data_access=True        
                else:
                    custom_data_access=False
            except MDT_Data_Access.DoesNotExist:
                custom_data_access=False
        except:
            custom_data_access=False
        
        if(faculty_advisor_access):
            return True
        elif(eb_access):
            return True
        elif(team_co_ordinator_access):
            return True
        elif(custom_data_access):
            return True
        else:
            return False
    
    def recruitment_session_view_access_control(username):
        '''in here all the username = ieee_id '''
        faculty_advisor_access=Access_Render.faculty_advisor_access(username=username)
        eb_access=Access_Render.eb_access(username=username)
        team_co_ordinator_access=Access_Render.team_co_ordinator_access(team_id=MDT_DATA.get_team_id(),username=username)
        custom_data_access=False
        try:
            try:
                c=MDT_Data_Access.objects.get(ieee_id=int(username))
                if(c.recruitment_session):
                    custom_data_access=True        
                else:
                    custom_data_access=False
            except MDT_Data_Access.DoesNotExist:
                custom_data_access=False
        except:
            custom_data_access=False
        
        if(faculty_advisor_access):
            return True
        elif(eb_access):
            return True
        elif(team_co_ordinator_access):
            return True
        elif(custom_data_access):
            return True
        else:
            return False
    def recruited_member_details_view_access(username):
        '''in here all the username = ieee_id '''
        faculty_advisor_access=Access_Render.faculty_advisor_access(username=username)
        eb_access=Access_Render.eb_access(username=username)
        team_co_ordinator_access=Access_Render.team_co_ordinator_access(team_id=MDT_DATA.get_team_id(),username=username)
        custom_data_access=False
        try:
            try:
                c=MDT_Data_Access.objects.get(ieee_id=int(username))
                if(c.recruited_member_details):
                    custom_data_access=True        
                else:
                    custom_data_access=False
            except MDT_Data_Access.DoesNotExist:
                custom_data_access=False
        except:
            custom_data_access=False
        
        if(faculty_advisor_access):
            return True
        elif(eb_access):
            return True
        elif(team_co_ordinator_access):
            return True
        elif(custom_data_access):
            return True
        else:
            return False
    
    def create_form_data_for_particular_renewal_session(renewal_session_id,form_description,ieee_membership_amount,ieee_ras_membership_amount,ieee_pes_membership_amount,ieee_ias_membership_amount,ieee_wie_membership_amount,bkash_payment_number,nagad_payment_number,further_contact_member_id):
        '''Creates and Updates Form data For Renewal Forms (Session Wise)'''
        create_form=Renewal_Form_Info(form_id=renewal_session_id, #in models the form id is primary key. Sending the renewal session id as primary key also to identify every form unique to a renewal session
                                      session=Renewal_Sessions.objects.get(id=renewal_session_id),
                                      form_description=form_description,
                                      ieee_membership_amount=ieee_membership_amount,
                                      ieee_ras_membership_amount=ieee_ras_membership_amount,
                                      ieee_pes_membership_amount=ieee_pes_membership_amount,
                                      ieee_ias_membership_amount=ieee_ias_membership_amount,
                                      ieee_wie_membership_amount=ieee_wie_membership_amount,
                                      bkash_payment_number=bkash_payment_number,
                                      nagad_payment_number=nagad_payment_number,
                                      further_contact_member_id=further_contact_member_id 
                                      
                                      )
        create_form.save()
        
    def load_form_data_for_particular_renewal_session(renewal_session_id):
        '''Loads data for paritcular renewal session. Takes the id of the renewal session as the parameter'''
        try:
            form_credentials=Renewal_Form_Info.objects.get(form_id=renewal_session_id)
            return form_credentials
        except Renewal_Form_Info.DoesNotExist:
            return False
        except:
            return False
    
    def load_officials_of_MDT():
        ''''''
        '''This function loads all the officials of mdt and returns a list of their ieee id'''
        load_incharges=Members.objects.filter(team=MDT_DATA.get_team_id(),position=10)
        load_co_ordinators=Members.objects.filter(team=MDT_DATA.get_team_id(),position=9)
        
        mdt_officials=[]
        for i in range(len(load_incharges)):
            mdt_officials.append(load_incharges[i])
        
        for i in range(len(load_co_ordinators)):
            mdt_officials.append(load_co_ordinators[i])
        
        return mdt_officials
    
    def add_member_to_data_access(ieee_id):
        try:
            if(MDT_Data_Access.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=MDT_Data_Access(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False
    def remove_member_from_data_access(ieee_id):
        try:
            MDT_Data_Access.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
    def add_member_to_team(ieee_id,position):
        team_id=MDT_DATA.get_team_id()
        Members.objects.filter(ieee_id=ieee_id).update(team=Teams.objects.get(id=team_id),position=Roles_and_Position.objects.get(id=position))
    
    def get_officials_access(ieee_id):
        ''''''
        try:
            ieee_id=str(ieee_id)
            load_member=Members.objects.get(ieee_id=ieee_id)
            print(load_member.position.id)
            if(load_member.position.id==10 or load_member.position.id==9):
                return True
            else:
                return False
        except:
            return False

            