from users.models import Members
from system_administration.models import adminUsers
from port.models import Roles_and_Position,Teams
import os
from django.conf import settings
from django.db import DatabaseError
from PIL import Image
from recruitment.models import recruitment_session,recruited_members
from central_branch.models import Events
from system_administration.render_access import Access_Render
from datetime import datetime
from django.db.models import Q
from users.models import User
from recruitment.models import recruited_members
import math
import sqlite3
from django.contrib import messages
from . models import Panel_Members,Alumni_Members
from port.models import Panels
import traceback
import logging
from system_administration.system_error_handling import ErrorHandling

class LoggedinUser:
    
    def __init__(self,user):
        '''Initializing loggedin user with current user from views'''
        self.user=user
    
    def getUserData(self):
        ieee_id=self.user.username
        try:
            get_Member_details=Members.objects.get(ieee_id=ieee_id)
            return {
            'name':get_Member_details.name,
            'position':get_Member_details.position,
            'team':get_Member_details.team,
            'ieee_id':get_Member_details.ieee_id,
            'email':get_Member_details.email_ieee,
            'nsu_id':get_Member_details.nsu_id,
            'ieee_email':get_Member_details.email_ieee,
            'email_personal':get_Member_details.email_personal,
            'home_address':get_Member_details.home_address,
            'contact_no':get_Member_details.contact_no,
            'dob':get_Member_details.date_of_birth,
            'gender':get_Member_details.gender,
            'major':get_Member_details.major,
            'joining_session':get_Member_details.session,
            'last_renewal':get_Member_details.last_renewal_session,
            'profile_picture':'/media_files/'+str(get_Member_details.user_profile_picture),
        
        }
        except Members.DoesNotExist:
            try:
                get_Member_details=adminUsers.objects.get(username=self.user.username) #getting data of the admin from database table. the admin must be in the database table.
                return {
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
def is_eb_or_admin(user):
    has_access = Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username)
    if has_access:
        return True
    else:
        return False
    
def get_all_registered_members(request):
    '''This function returns all the INSB members registered in the main database'''
    try:
        get_members=Members.objects.filter().all().order_by('position')
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

def getTypeOfEventStats():

    '''This fucntion is for the circular chart that shows the total events of each type
    and their corresponding percentages on poral'''

    event_stats_keys =[]
    event_stats_values=[]
    # all_event_type=Event_type.objects.all()
    all_events_number = Events.objects.all().count()
    event_percentage ={}
    # for i in all_event_type:
    #     event_count = Events.objects.filter(event_type = i.pk).count()
    #     try:
    #         percentage = (event_count/all_events_number*1.0)*100
    #         percentage = round(percentage,1)
    #         event_stats_keys.append(i.event_type)
    #         event_stats_values.append(event_count)
    #         event_percentage.update({i.event_type:percentage})
    #     except:
    #         pass
    return event_stats_keys,event_stats_values,event_percentage


def getEventNumberStat():

    '''Returns a dictionary that counts the number of all events that occured over the past
    5 years including current year'''

    event_num = []
    year = datetime.date.today().year
    print(year)
    for i in range(5):
        count = Events.objects.filter(event_date__year=(year-i)).count()
        event_num.append(count)
    event_num.reverse()
    return event_num

import datetime
def getEventNumberStatYear():

    '''Return the last 5 years including today as a list, so that it could be
    displayed for the x-axis values on the graph in the django template for the
    chart 'Event for 6 years' '''
    
    year_list =[]
    year = datetime.date.today().year
    for i in range(5):
        year_list.append(year-i)
    year_list.reverse()
    return year_list

def getHitCountMonthly():
    '''
    For the time being shows monthly hit page count only which is seen on the Page visitor chart'''
    daily = []
    days_of_month=[]
    for i in range(31):
        number_of_people_per_day = User.objects.filter(Q(created_at__day=(i+1)), Q(created_at__month=datetime.datetime.now().month), Q(created_at__year=datetime.datetime.now().year)).count()   
        if number_of_people_per_day>0:
            daily.append(number_of_people_per_day)
            days_of_month.append(i+1)

    monthly_visitor=getMonthName(datetime.datetime.now().month)
    return monthly_visitor,days_of_month,daily

def getHitCountYearly():

    '''This function returns the total numbers of visitors on main website per month'''
    monthly=[]
    month_names = []
    for i in range(12):
        number_of_people_per_month = User.objects.filter(Q(created_at__month = (i+1)), Q(created_at__year=datetime.datetime.now().year)).count()
        if number_of_people_per_month>0:
            monthly.append(number_of_people_per_month)
            month_names.append(getMonthName(i+1)[0:3])
    year = datetime.datetime.now().year
    return year,month_names,monthly

def getHitCountOver5Years():
    '''This function returns the number of visitors on the main webstire over 5 years'''
    yearly=[]
    current_year = datetime.datetime.now().year
    for i in range(5):
        number_of_people_over_5_years = User.objects.filter(created_at__year=(current_year-i)).count()
        yearly.append(number_of_people_over_5_years)
    yearly.reverse()
    return yearly




def getMaleFemaleRationAndActiveStatusStats():

    '''This function is for the seconf circular chart'''

    all_females = Members.objects.filter(gender="Female").count()
    all_males = Members.objects.filter(gender="Male").count()
    active_members = recruited_members.objects.filter(ieee_payment_status=True).count()
    inactive_members = recruited_members.objects.all().count() - active_members
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


    

class PanelMembersData:
    logger=logging.getLogger(__name__)

    def add_members_to_branch_panel(request,members,position,panel_info,team_primary):

        try:
            for i in members:
                # check if Member already exists in the Panel
                check_member=Panel_Members.objects.filter(tenure=panel_info.pk,member=i).exists()
                if(check_member):
                    # update Members Position and Teams
                    Panel_Members.objects.filter(tenure=panel_info.pk,member=i).update(position=Roles_and_Position.objects.get(id=position),team=Teams.objects.get(primary=team_primary))
                    messages.info(request,f"{i} already existed in the Panel. Positions and Team were updated.")
                    return True
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
            # Delete from panel members database
            Panel_Members.objects.filter(tenure=Panels.objects.get(id=panel_id),member=Members.objects.get(ieee_id=ieee_id)).delete()

            # Remove Positions from Members Table database,turing their position in general members
            Members.objects.filter(ieee_id=ieee_id).update(position=Roles_and_Position.objects.get(id=13),team=None)
            messages.info(request,f"{ieee_id} was removed from the Panel")
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
            messages.error(request,"Can not add alumni to Branch Panel. Something went wrong!")
            return False
            
            
    def remove_alumns_from_branch_panel(request,member_to_remove,panel_id):
        '''Removes Alumni Member from Branch panel. Gets the tenure id, and the Member id from Panel Members table'''
        try:
            member_to_remove = Panel_Members.objects.get(pk=member_to_remove,tenure=panel_id)
            messages.error(request,f"{member_to_remove.ex_member.name} was removed from the panel.")
            member_to_remove.delete()
            return True
        except Exception as e:
            PanelMembersData.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not remove alumni from Branch Panel. Something went wrong!")
            return False

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

      
    

