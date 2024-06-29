from notification.models import MemberNotifications
from task_assignation.models import Member_Task_Point
from users.models import Members,MemberSkillSets
from system_administration.models import adminUsers
from port.models import Roles_and_Position, SkillSetTypes,Teams
import os
from django.conf import settings
from django.db import DatabaseError
from PIL import Image
from recruitment.models import recruitment_session,recruited_members
from central_events.models import Events,Event_Category,InterBranchCollaborations
from system_administration.render_access import Access_Render
from django.db.models import Q
from users.models import User_IP_Address
from recruitment.models import recruited_members
import math
from membership_development_team.renderData import MDT_DATA
import sqlite3
from django.contrib import messages
from . models import Panel_Members,Alumni_Members
from port.models import Panels
import traceback
import logging
from system_administration.system_error_handling import ErrorHandling
from system_administration.render_access import Access_Render
from chapters_and_affinity_group.get_sc_ag_info import SC_AG_Info
import calendar
from datetime import datetime
from port.renderData import PortData
from functools import wraps
from django.contrib.auth.models import User,auth
from django.shortcuts import render,redirect
from django.utils.dateformat import format

class LoggedinUser:
    
    def __init__(self,user):
        '''Initializing loggedin user with current user from views'''
        self.user=user
    
    def getUserData(self):
        ieee_id=self.user.username
        try:
            get_Member_details=Members.objects.get(ieee_id=ieee_id)
            try:
                member_notifications = MemberNotifications.objects.filter(member=get_Member_details).order_by('-notification__timestamp')[:3]
                latest_notification_timestamp = MemberNotifications.objects.filter(member=get_Member_details).order_by('-notification__timestamp').first()
                latest_notification_timestamp = latest_notification_timestamp.notification.timestamp
                latest_notification_timestamp = format(latest_notification_timestamp, 'Y-m-d\\TH:i:s')
                unread_notification_count = MemberNotifications.objects.filter(member=get_Member_details,is_read = False).order_by('-notification__timestamp').count()
            except:
                member_notifications = None
                latest_notification_id = None
                unread_notification_count = 0
            return {
            'is_admin_user': False,
            'name':get_Member_details.name,
            'position':get_Member_details.position,
            'team':get_Member_details.team,
            'ieee_id':get_Member_details.ieee_id,
            'email_nsu':get_Member_details.email_nsu,
            'nsu_id':get_Member_details.nsu_id,
            'email_ieee':get_Member_details.email_ieee,
            'email_personal':get_Member_details.email_personal,
            'home_address':get_Member_details.home_address,
            'contact_no':get_Member_details.contact_no,
            'dob':get_Member_details.date_of_birth,
            'gender':get_Member_details.gender,
            'major':get_Member_details.major,
            'joining_session':get_Member_details.session,
            'last_renewal':get_Member_details.last_renewal_session,
            'facebook_url':get_Member_details.facebook_url,
            'linkedin_url':get_Member_details.linkedin_url,
            'profile_picture':'/media_files/'+str(get_Member_details.user_profile_picture),
            'notifications':member_notifications,
            'latest_timestamp':latest_notification_timestamp,
            'unread_notification_count':unread_notification_count,
        }
        except Members.DoesNotExist:
            try:
                get_Member_details=adminUsers.objects.get(username=self.user.username) #getting data of the admin from database table. the admin must be in the database table.
                return {
                'is_admin_user': True,
                'name':get_Member_details.name,
                'email':get_Member_details.email,
                'profile_picture':'/media_files/'+str(get_Member_details.profile_picture),
                }           
            except adminUsers.DoesNotExist:
                return False
        except ValueError:
            try:
                get_Member_details=adminUsers.objects.get(username=self.user.username)
                return {
                'is_admin_user': True,
                'name':get_Member_details.name,
                'email':get_Member_details.email,
                'profile_picture':'/media_files/'+str(get_Member_details.profile_picture),
                }
            except adminUsers.DoesNotExist:
                return False
    
    
    def change_profile_picture(self,picture_file):
        try:
            #get user firs with the username=ieee_id for general users
            get_user=Members.objects.get(ieee_id=self.user.username)
            
            #get the previous profile picture of the user to delete it later
            previous_profile_picture=settings.MEDIA_ROOT+str(get_user.user_profile_picture)
            #check if the previous profile picture is the default one, if yes, just replace with new one. if no, delete the previous profile picture. replace with new one
            if(previous_profile_picture!=(settings.MEDIA_ROOT+'user_profile_pictures/default_profile_picture.png')):
                
                if(os.path.isfile(previous_profile_picture)): #checking if file exists
                    
                    try:
                        #removing the profile picture from system
                        os.remove(previous_profile_picture)
                        
                        #update new profile picture
                        get_user.user_profile_picture=picture_file
                        get_user.save()
                        return True
                    except OSError:
                        return False

                else: #if file does not exist for any reason, just update the profile picture
                    get_user.user_profile_picture=picture_file
                    get_user.save()
                    return True
            
            else:
                
                #normally just update the profile picture, not deletinf the default one
                get_user.user_profile_picture=picture_file
                get_user.save()
                return True
                
        except Members.DoesNotExist:
            try:
                #DO THE SAME WORK DONE ABOVE, BUT JUST WITH THE ADMIN DATABASE NOW
                get_user=adminUsers.objects.get(username=self.user.username)
                previous_profile_picture=settings.MEDIA_ROOT+str(get_user.profile_picture)
                
                if(previous_profile_picture!=(settings.MEDIA_ROOT+'Admin/admin_profile_pictures/default_profile_picture.png')):
                    
                    if(os.path.isfile(previous_profile_picture)):
                        try:
                            os.remove(previous_profile_picture)
                            get_user.profile_picture=picture_file
                            get_user.save()
                            return True
                        except OSError:
                            return False
                    else:
                        get_user.profile_picture=picture_file
                        get_user.save()
                        return True
                else:
                    get_user.profile_picture=picture_file
                    get_user.save()
                    return True
                
            except adminUsers.DoesNotExist:
                return False 
        
        except ValueError:
            try:
                #DO THE SAME WORK DONE ABOVE, BUT JUST WITH THE ADMIN DATABASE NOW
                get_user=adminUsers.objects.get(username=self.user.username)
                previous_profile_picture=settings.MEDIA_ROOT+str(get_user.profile_picture)
                
                if(previous_profile_picture!=(settings.MEDIA_ROOT+'Admin/admin_profile_pictures/default_profile_picture.png')):
                    
                    if(os.path.isfile(previous_profile_picture)):
                        try:
                            os.remove(previous_profile_picture)
                            get_user.profile_picture=picture_file
                            get_user.save()
                            return True
                        except OSError:
                            return False
                    else:
                        get_user.profile_picture=picture_file
                        get_user.save()
                        return True
                else:
                    get_user.profile_picture=picture_file
                    get_user.save()
                    return True
                
            except adminUsers.DoesNotExist:
                return False
    
    def update_user_data(self, name, nsu_id, home_address, date_of_birth, email_personal, gender, email_nsu, email_ieee, contact_no, major, facebook_url, linkedin_url):
        ''' This function updates the user profile information. It takes name, nsu_id, home_address, date_of_birth, email_personal, gender, email_nsu, email_ieee, contact_no, major, facebook_url and linkedin_url '''
        try:
            #Get user details from database
            get_user=Members.objects.filter(ieee_id=self.user.username)
            #Update the user profile information
            get_user.update(name=name,
                            nsu_id=nsu_id,
                            home_address=home_address,
                            date_of_birth=date_of_birth,
                            email_personal=email_personal,
                            gender=gender,
                            email_nsu=email_nsu,
                            email_ieee=email_ieee,
                            contact_no=contact_no,
                            major=major,
                            facebook_url=facebook_url,
                            linkedin_url=linkedin_url)           
            return True
        except Members.DoesNotExist:
            return False
        
    def update_admin_user_data(self, name, email):
        ''' This function updates the admin user profile information. It takes a name and an email only '''
        try:
            #Get admin user details from database
            get_user=adminUsers.objects.filter(username=self.user.username)
            #Update the admin user profile information
            get_user.update(name=name, email=email)
            return True
        except adminUsers.DoesNotExist:
            return False

def is_eb_or_admin(user):
    has_access = Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username)
    if has_access:
        return True
    else:
        return False

def member_login_permission(view_func):

    '''This function checks if user is restricted to log in or not'''

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user.username
        if Access_Render.system_administrator_superuser_access(user) or Access_Render.system_administrator_staffuser_access(user) or Access_Render.faculty_advisor_access(user):
            return view_func(request, *args, **kwargs)
        else:
            user = Members.objects.get(ieee_id = int(user))
            if user.is_blocked:
                auth.logout(request)
                messages.error(request, 'Your account has been blocked by Administrator. If you are not supposed to receive this message please contact IEEE NSU SB membership development team')
                return redirect('users:login')
            return view_func(request, *args, **kwargs)
    return _wrapped_view

def get_all_registered_members(request):
    '''This function returns all the INSB members registered in the main database'''
    try:
        get_members=Members.objects.filter().all().order_by('position__rank')
        return get_members
    except sqlite3.DatabaseError:
        messages.error(request,"An internal Database Error has occured!")
    except:
        messages.error(request,"Soemthing went wrong. Please try again!")
        

def getRecruitmentStats():    
    """Returns a lists of the recruitment stats for the last 5 sessions.
    Return the seesion name and the number of people per session in seperate lists"""

    recruitment_stats_key=[]
    recruitment_stats_values=[]
    
    try:
        for i in recruitment_session.objects.all().order_by('-id')[:5]:
            recruitee_count=recruited_members.objects.filter(session_id=i.id).count()
            recruitment_stats_key.append(i.session)
            recruitment_stats_values.append(recruitee_count)
        return recruitment_stats_key,recruitment_stats_values
    except:
        return False  

def getTypeOfEventStats(request,primary):

    '''This fucntion is for the circular chart that shows the total events of each type
    and their corresponding percentages on poral. It shows event type for societies'''

    event_stats_keys =[]
    event_stats_values=[]
    #getting the society
    society = SC_AG_Info.get_sc_ag_details(request,primary)
    #intialiing empty lists and dictionaries
    dic={}
    event_percentage ={}
    event_stats_keys=[]
    event_stats_values=[]
    #getting all events of society
    all_events_of_society = Events.objects.filter(publish_in_main_web = True,event_organiser = society)
    #getting the collaborated events of this society
    collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
    #joining them
    all_events_with_collbaration = all_events_of_society.union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True))
    #appending in dictionary the event type as key and the number found
    for event in all_events_with_collbaration:
        for event_cate in event.event_type.all():
            if event_cate.event_category not in dic:
                dic[event_cate.event_category]=0
            dic[event_cate.event_category]+=1
    #finding the number of all events with collaboration
    all_events_with_collbaration_count = len(all_events_with_collbaration)
    #now appending the key and value in corresponding lists and dictionary
    for key,value in dic.items():
        percentage = (value/all_events_with_collbaration_count*1.0)*100
        percentage = round(percentage,1)
        event_stats_keys.append(key)
        event_stats_values.append(value)
        event_percentage.update({key:percentage})

    return event_stats_keys,event_stats_values,event_percentage


def getEventNumberStat(request,primary):

    '''Returns two list. First is the year list and second one is the event number
        that occured in those years'''
    #getting the society
    society = SC_AG_Info.get_sc_ag_details(request,primary)
    #initializing empty list
    event_num = []
    #getting current year
    year = datetime.date.today().year
    #getting all events of society
    all_events_of_society = Events.objects.filter(publish_in_main_web = True,event_organiser = society)
    #getting the collaborated events of this society
    collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
    all_events_with_collbaration = all_events_of_society.union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True))
    #making query set as list
    events = list(all_events_with_collbaration)
    #iterating over the year
    for i in range(5):
        #variable to count
        count=0
        #making a copy to avoid iterating issue
        events_copy = events.copy()
        for event in events_copy:
            #when event year is found removing increasing count value and removing it from list 
            #to loawer time complexity
            try:
                if event.event_date.year == year-i:
                    count+=1
                    events.remove(event)
            except:
                pass
        #assiging the number of events occured in a year to the list
        event_num.append(count)
    #reversing list to get the oldest count first and lasted count last
    event_num.reverse()
    year_list=getEventNumberStatYear()
    return year_list,event_num

import datetime
def getEventNumberStatYear():

    '''Return the last 5 years including today as a list, so that it could be
    displayed for the x-axis values on the graph in the django template for the
    chart 'Event for 5 years' '''
    
    year_list =[]
    #getting current year
    year = datetime.date.today().year
    for i in range(5):
        #basically getting the last five years 'year number'
        year_list.append(year-i)
    #reversing to get oldest one first and lasted (which is current year) last
    year_list.reverse()
    return year_list

def getHitCountMonthly():
    '''
    For the time being shows monthly hit page count only which is seen on the Page visitor chart'''
    #daily list holds the number of people that visited the website on a specific date
    #days_of_month list holds the dates on which there is atleast one visitor on the main web page
    daily = []
    days_of_month=[]

    current_date = datetime.datetime.now()
    year = current_date.year
    month = current_date.month
    # Get the number of days in the current month
    num_days_in_month = calendar.monthrange(year, month)[1]
  
    for i in range(num_days_in_month):
        #getting number of people on each day from database
        number_of_people_per_day = User_IP_Address.objects.filter(Q(created_at__day=(i+1)), Q(created_at__month=datetime.datetime.now().month), Q(created_at__year=datetime.datetime.now().year)).count()   
        if number_of_people_per_day>0:
            #if there is visitor then it is appended to the list else not because showing all
            #dates of a month on the page looks bad. So needs styling
            #TODO: need styling
            daily.append(number_of_people_per_day)
            days_of_month.append(i+1)

    month_name=datetime.datetime.now().strftime("%B")
    return month_name,days_of_month,daily

def getHitCountYearly():

    '''This function returns the total numbers of visitors on main website per month'''
    monthly=[]
    month_names = []
    for i in range(12):
        #getting the total number of people visited the main website in a single month. And this is 
        #repeated for every month
        number_of_people_per_month = User_IP_Address.objects.filter(Q(created_at__month = (i+1)), Q(created_at__year=datetime.datetime.now().year)).count()
        #if there are no people registered in a month then not appended
        #TODO: need styling
        if number_of_people_per_month>0:
            monthly.append(number_of_people_per_month)
        else:
            monthly.append(0) 
        month_names.append(getMonthName(i+1)[0:3])
    year = datetime.datetime.now().year
    return year,month_names,monthly

def getHitCountOver5Years():
    '''This function returns the number of visitors on the main webstire over 5 years'''
    yearly=[]
    current_year = datetime.datetime.now().year
    for i in range(5):
        #getting the total number of people that visited the main website in a single month.
        number_of_people_over_5_years = User_IP_Address.objects.filter(created_at__year=(current_year-i)).count()
        yearly.append(number_of_people_over_5_years)
    yearly.reverse()
    return yearly




def getMaleFemaleRationAndActiveStatusStats():

    '''This function is for the second circular chart'''

    all_females = Members.objects.filter(gender="Female").count()
    all_males = Members.objects.filter(gender="Male").count()
    active_members = Members.objects.filter(is_active_member=True).count()
    inactive_members = Members.objects.all().count() - active_members
    total_members = Members.objects.all().count()
    total_list_keys = ['Males','Females','Active Members','Inactive Members']
    total_list_values = [all_males,all_females,active_members,inactive_members]
    dic = {
        'Males':(round(((all_males/total_members*1.0)*100),1)),
        'Females':(round(((all_females/total_members*1.0)*100),1)),   
        'Active Members':(round(((active_members/total_members*1.0)*100),1)),
        'Inactive Members': (round(((inactive_members/total_members*1.0)*100),1))
    } 
    return total_list_keys,total_list_values,dic

def getMonthName(numb: int)->str:

    '''Returns month name according to input value'''

    if numb == 1:
        return "January"
    elif numb==2:
        return "February"
    elif numb==3:
        return "March"
    elif numb==4:
        return "April"
    elif numb==5:
        return "May"
    elif numb==6:
        return "June"
    elif numb==7:
        return "July"
    elif numb==8:
        return "August"
    elif numb==9:
        return "September"
    elif numb==10:
        return "October"
    elif numb==11:
        return "November"
    elif numb==12:
        return "December"

def getMonthlyTopMembers():
    ''' This functions returns a list of all members who has the highest task points completed in that month '''

    monthly_members = Member_Task_Point.objects.all().order_by('-completion_points','member')
    monthly_top_members = {}

    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year

    for member in monthly_members :
        if member.completion_date and member.completion_date.month == current_month and member.completion_date.year == current_year:
            if (not member.member in monthly_top_members.keys()):
                monthly_top_members[member.member] = [Members.objects.get(ieee_id=member.member), member.completion_points]
            else:
                monthly_top_members[member.member][1] += member.completion_points
    
    return list(monthly_top_members.values())

def add_new_skill_type(request,skill_type):
    try:
        new_skill_type=SkillSetTypes.objects.create(skill_type=skill_type)
        new_skill_type.save()
        messages.success(request,"New Skillset type was added.")
        return True
    except Exception as e:
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        messages.error(request,"Something went wrong while adding new skill type")
        return False

def load_all_skill_types(request):
    try:
        all_skills=SkillSetTypes.objects.all()
        return all_skills
    except Exception as e:
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        messages.error(request,"Something went wrong while loading all skill type")
        return False

    

class PanelMembersData:
    logger=logging.getLogger(__name__)

    def get_eb_members_from_branch_panel(request,panel):
        '''This method gets all the EB members from the panel of branch and returns them in a list'''
        try:
            # get panel
            get_panel=Panels.objects.get(pk=panel)
            get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=get_panel.pk))
            eb_member=[]
            for i in get_panel_members:
                if(i.member is not None):
                    if(i.position.is_eb_member):
                        eb_member.append(i)
            return eb_member
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Something went wrong while loading Executive Members")
    
    def get_officer_members_from_branch_panel(request,panel):
        '''This method gets all the Officer members from the panel of branch and returns them in a list'''
        try:
            # get panel
            get_panel=Panels.objects.get(pk=panel)
            get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=get_panel.pk))
            officer_member=[]
            for i in get_panel_members:
                if(i.position.is_officer):
                    officer_member.append(i)
            return officer_member
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Something went wrong while loading Officer Members")
    
    
    def get_members_of_teams_from_branch_panel(request,panel_id,team_primary):
        '''this method gets all the members associated with a team within the current panel'''
        try:
            get_panel=Panels.objects.get(pk=panel_id)
            get_panel_members_of_team=Panel_Members.objects.filter(tenure=get_panel.pk,team=Teams.objects.get(primary=team_primary))
            return get_panel_members_of_team
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Something went wrong while loading Officer Members")
     
        
            
    def get_volunteer_members_from_branch_panel(request,panel):
        '''This method gets all the Volunteer members from the panel of branch and returns them in a list'''
        try:
            # get panel
            get_panel=Panels.objects.get(pk=panel)
            get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=get_panel.pk))
            volunteer_member=[]
            for i in get_panel_members:
                if(not i.position.is_officer and not i.position.is_eb_member and not i.position.is_co_ordinator and not i.position.is_faculty and not i.position.is_mentor and not i.position.is_sc_ag_eb_member):
                    volunteer_member.append(i)
            return volunteer_member
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Something went wrong while loading Officer Members")
    
    def get_alumni_members_from_panel(request,panel):
        '''This method gets all the Alumni members from the panel of branch and returns them in a list'''
        try:
            # get panel
            get_panel=Panels.objects.get(pk=panel)
            get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=get_panel.pk))
            alumni_member=[]
            for i in get_panel_members:
                if(i.member is None): #as alumni member has no registered IEEE ID
                    alumni_member.append(i)
            return alumni_member
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Something went wrong while loading Officer Members")
    
    def add_members_to_branch_panel(request,members,position,panel_info,team_primary):
        try:
            for i in members:
                # check if Member already exists in the Panel
                check_member=Panel_Members.objects.filter(tenure=panel_info.pk,member=i).exists()
                if(check_member):
                    # update Members Position and Teams in current panel
                    Panel_Members.objects.filter(tenure=panel_info.pk,member=i).update(position=Roles_and_Position.objects.get(id=position),team=Teams.objects.get(primary=team_primary))
                    messages.info(request,f"{i} already existed in the Panel. Positions and Team were updated.")
                # if not then add members to the Panel members table
                else:
                    new_panel_member=Panel_Members.objects.create(tenure=Panels.objects.get(id=panel_info.pk),member=Members.objects.get(ieee_id=i),position=Roles_and_Position.objects.get(id=position),team=Teams.objects.get(primary=team_primary))
                    new_panel_member.save()

                # then update the members team and position in Members table if the panel is current only
                if(panel_info.current):
                    Members.objects.filter(ieee_id=i).update(team=Teams.objects.get(primary=team_primary),position=Roles_and_Position.objects.get(id=position))
                    messages.info(request,"Member was updated in the Team Page")
            messages.success(request,"Members were added in the Panel")
            return True
        except sqlite3.OperationalError:
            messages.error(request,"An internal Database error has occured!")
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Something went wrong! Please try again!")
            
    
    def remove_member_from_panel(request,ieee_id,panel_id):
        
        try:
            print(panel_id)
            # Delete from panel members database
            Panel_Members.objects.filter(tenure=Panels.objects.get(id=panel_id),member=Members.objects.get(ieee_id=ieee_id)).delete()
            # Remove Positions from Members Table database,turing their position in general members
            Members.objects.filter(ieee_id=ieee_id).update(position=Roles_and_Position.objects.get(id=13),team=None)
            messages.info(request,f"{ieee_id} was removed from the Panel and Teams")
            return True
        except sqlite3.OperationalError:
            messages.error(request,"An internal Database error has occured!")
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Something went wrong! Please try again!")

    
    def add_alumns_to_branch_panel(request,alumni_id,panel_id,position):
        '''Adds alumni members to the panels. As INSB Stores data of Alumnis that were Executives we will only store Executive Alumns'''
        try:
            get_alumni=Alumni_Members.objects.get(pk=alumni_id)
            get_panel=Panels.objects.get(pk=panel_id)
            
            # check if alumni exists in the panel
            check_alum=Panel_Members.objects.filter(tenure=get_panel.pk,ex_member=get_alumni.pk).exists()
            if(not check_alum):
                new_panel_member=Panel_Members.objects.create(
                    tenure=Panels.objects.get(pk=get_panel.pk),
                    ex_member=Alumni_Members.objects.get(pk=get_alumni.pk),
                    position=Roles_and_Position.objects.get(id=position),
                    team=Teams.objects.get(primary=1) #As branch panel
                )
                new_panel_member.save()
                return True
            else:
                Panel_Members.objects.filter(tenure=get_panel.pk,ex_member=get_alumni.pk).update(position=Roles_and_Position.objects.get(id=position))
                messages.info(request,f"Alumni member {get_alumni.name} already existed in the panel. However, Member's position was updated.")
                return True
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not add alumni to the Panel. Something went wrong!")
            return False
    
           
            
    def remove_alumns_from_branch_panel(request,member_to_remove,panel_id):
        '''Removes Alumni Member from Branch panel. Gets the panel id, and the Member id from Panel Members table'''
        try:
            member_to_remove = Panel_Members.objects.get(pk=member_to_remove,tenure=panel_id)
            messages.warning(request,f"{member_to_remove.ex_member.name} was removed from the panel.")
            member_to_remove.delete()
            return True
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not remove alumni from Branch Panel. Something went wrong!")
            return False
    
    def get_sc_ag_members_from_current_panel(request,sc_ag_primary):
        # returns all the members of the current panel of sc_ag
        try:
            get_current_panel_of_sc_ag=PortData.get_sc_ag_current_panel(request=request,sc_ag_primary=sc_ag_primary)
            if(get_current_panel_of_sc_ag is not None):
                get_current_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=get_current_panel_of_sc_ag.pk))
                return get_current_panel_members
            else:
                return None      
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            # ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return None
    
    def get_sc_ag_members_from_panel(request,panel_pk):
        # returns all the members of the given panel
        try:
            get_all_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=panel_pk))

            if get_all_members is not None:
                return get_all_members
            else:
                return None
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            # ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return None
        
class Alumnis:
    logger=logging.getLogger(__name__)
    
    def create_alumni_members(request,name,picture,linkedin_link,facebook_link,email,contact_no):
        try:
            # if picture was uploaded
            if picture is not None:
                new_alumni=Alumni_Members.objects.create(
                    name=name,
                    picture=picture,
                    linkedin_link=linkedin_link,
                    facebook_link=facebook_link,
                    email=email,
                    contact_no=contact_no
                )
                new_alumni.save()
                messages.success(request,"Alumni Member created successfully")
                return True
            else:
                new_alumni=Alumni_Members.objects.create(
                    name=name,
                    linkedin_link=linkedin_link,
                    facebook_link=facebook_link,
                    email=email,
                    contact_no=contact_no
                )
                new_alumni.save()
                messages.success(request,"Alumni Member created successfully")
                return True
            
        except Exception as e:
            Alumnis.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Something went wrong! Please Try again!")
            return False

    
    def getAllAlumns():
        '''gets all the alumnis and returns the list of all alumnis, mainly returns pk'''
        try:
            alumni_list = Alumni_Members.objects.all().order_by('-pk')
            return alumni_list
        except Exception as e:
            Alumnis.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        