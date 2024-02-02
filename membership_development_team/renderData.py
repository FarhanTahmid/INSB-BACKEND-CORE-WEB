from . models import Renewal_Form_Info,Renewal_Sessions
from membership_development_team.models import Renewal_requests
from users.models import Members
from port.models import Teams,Roles_and_Position
from system_administration.models import MDT_Data_Access
from system_administration.render_access import Access_Render
from datetime import date
from datetime import datetime,timedelta,time
from central_branch import renderData
from django_celery_beat.models import ClockedSchedule,PeriodicTask
import json
from zoneinfo import ZoneInfo

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
    
    def get_all_team_members():
        '''Returns MDT Team Members with positions'''
        team_members=renderData.Branch.load_team_members(team_primary=7)
        co_ordinators=[]
        incharges=[]
        core_volunteers=[]
        team_volunteers=[]
        for i in team_members:
            if(i.position.is_officer):
                if(i.position.is_co_ordinator):
                    co_ordinators.append(i)
                else:
                    incharges.append(i)
            elif(i.position.is_volunteer):
                if(i.position.is_core_volunteer):
                    core_volunteers.append(i)
                else:
                    team_volunteers.append(i)
        return co_ordinators,incharges,core_volunteers,team_volunteers
    
    
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
        # function works fine
        '''This function loads all the team members for membership development team'''

        load_team_members=renderData.Branch.load_team_members(team_primary=7)
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
    
    def create_form_data_for_particular_renewal_session(renewal_session_id,form_description,ieee_membership_amount,ieee_ras_membership_amount,ieee_pes_membership_amount,ieee_ias_membership_amount,ieee_wie_membership_amount,bkash_payment_number,nagad_payment_number,further_contact_member_id,accepting_response):
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
                                      further_contact_member_id=further_contact_member_id,
                                      accepting_response=accepting_response)
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
        '''This function loads all the officials of mdt and returns a list of their ieee id'''
        team_members=renderData.Branch.load_team_members(team_primary=7)
        officers=[]
        for i in team_members:
            if(i.position.is_officer):
                officers.append(i)
        return officers
    
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
        try:
            renderData.Branch.add_member_to_team(ieee_id=ieee_id,position=position,team_primary=7)
            return True
        except:
            return False
    
    
    def process_renewal_item_dict(renewal_check_dict,request_id,form_id):
        renewal_list=[]
        for key in renewal_check_dict:
            if(renewal_check_dict[key]==True):
                renewal_list.append(key)
        
        
        renewal_amount_dict={
            'IEEE Membership':MDT_DATA.getPaymentAmount(request_id=request_id,info='ieee',form_id=form_id),
            'IEEE PES Membership':MDT_DATA.getPaymentAmount(request_id=request_id,info='pes',form_id=form_id),
            'IEEE RAS Membership':MDT_DATA.getPaymentAmount(request_id=request_id,info='ras',form_id=form_id),
            'IEEE IAS Membership':MDT_DATA.getPaymentAmount(request_id=request_id,info='ias',form_id=form_id),
            'IEEE WIE Membership':MDT_DATA.getPaymentAmount(request_id=request_id,info='wie',form_id=form_id),
        }
        total_amount=(
            renewal_amount_dict['IEEE Membership']+
            renewal_amount_dict['IEEE PES Membership']+
            renewal_amount_dict['IEEE RAS Membership']+
            renewal_amount_dict['IEEE IAS Membership']+
            renewal_amount_dict['IEEE WIE Membership']
        )
        return renewal_list,total_amount
    
    def check_active_members(self):
        
        all_users = Members.objects.all()
        if len(all_users) == 0:
            pass
        else:
            for member in all_users:
                is_active = MDT_DATA.get_member_account_status(member.ieee_id)

                if is_active:
                    member.is_active_member = True
                    member.save()
    
    def loadMdtFirstCoordinator():
        laod_team_official=MDT_DATA.get_all_team_members()
        co_ordinators=laod_team_official[0]
        if(len(co_ordinators)>0):
            return co_ordinators[0]
        return False
    
    def wish_members_birthday(self):

        '''This function will run everday around 12:00 am to check which members
        have birthday on the following day to greet them'''
        #gettting todays date
        today = datetime.now()
        #scheduling it to be sent at 12:00 AM
        scheduled_email_date_time = today
        #getting all members
        all_members = Members.objects.all()
        #creating instance of schedule 
        clocked,created = ClockedSchedule.objects.get_or_create(clocked_time=scheduled_email_date_time)

        for members in all_members:  
            if members.date_of_birth:
                #only getting registered if there are birthdays tomorrow
                if members.date_of_birth.day == today.day and members.date_of_birth.month == today.month:
                    #assigning unique id
                    scheduled_email_id = f"{members.nsu_id}_{scheduled_email_date_time}"
                    #providing email details
                    subject="Birthday Greetings from IEEE NSU Student Branch."
                    mail_body =f"""
                    
Dear {members.name},

Wishing you a very happy birthday on behalf of IEEE NSU Student Branch. On your birthday we wish you all the success and happiness on your upcoming future and prospects.

Birthdays are always special for every individual and having your grace brings not only bliss but your contributions are what makes IEEE NSU SB thrive for more. May it be a joyful celebration of your achievements and a reminder of the positive impact you've made. Wishing you continued success, happiness, and fulfillment in every step of your journey.
Enjoy every moment of your special day and make wonderful memories that will last a lifetime. Here's to another year of growth, friendship, and success!

Once again,
Happy Birthday! 🎉🎂

Best regards,
From every individuals of IEEE NSU SB community."""

                    email_list = []
                    email_list.append(members.email_nsu)
                    email_list.append(members.email_personal)
                    to_email_list = json.dumps(email_list)

                    PeriodicTask.objects.create(
                        clocked = clocked,
                        name = scheduled_email_id,
                        task = "users.tasks.send_birthday_wish_email",
                        args =json.dumps([to_email_list,subject,mail_body]),
                        one_off = True,
                        enabled = True,
                    )

               
        



                
        
            

