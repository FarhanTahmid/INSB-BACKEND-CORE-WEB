from .models import HomePageTopBanner,BannerPictureWithStat
from django.http import HttpResponseServerError
from users.models import Members,User_IP_Address
from membership_development_team.renderData import MDT_DATA
from central_events.models import Events
from port.models import Chapters_Society_and_Affinity_Groups
from graphics_team.models import Graphics_Banner_Image
from media_team.models import Media_Images
from datetime import datetime
import traceback
from system_administration.system_error_handling import ErrorHandling
import logging
from django.contrib import messages
from django.utils import timezone
class HomepageItems:

    logger=logging.getLogger(__name__)

    def load_all_events(flag):
        try:
            current_datetime = timezone.now()
            dic = {}
            if flag:
                events =  Events.objects.filter(publish_in_main_web= True).order_by('-event_date')
            else:
                events = Events.objects.filter(publish_in_main_web= True,event_date__gt=current_datetime).order_by('event_date')[:5]
                print(events)
            for i in events:
                try:
                    event = Graphics_Banner_Image.objects.get(event_id = i.pk)
                    dic[i]=event.selected_image
                except:
                    dic[i] = "#"
            return dic
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def load_event_banner_image(event_id):
            try:
                return Graphics_Banner_Image.objects.get(event_id = event_id).selected_image
            except:
                return None
    
    def load_event_gallery_images(event_id):

        return Media_Images.objects.filter(event_id = event_id)

        



    def getHomepageBannerItems():
        
        try:
            return HomePageTopBanner.objects.all()
            
        except Exception as e:
            print(e)
            response = HttpResponseServerError("Oops! Something went wrong.")
            return response
    
    def getBannerPictureWithStat():

        try:
            getItem=BannerPictureWithStat.objects.first()
            return getItem.image
        except Exception as e:
            print(e)
            response = HttpResponseServerError("Oops! Something went wrong.")
            return response
        
    def getAllIEEEMemberCount():
        '''Gets all the count of members in Database'''
        return Members.objects.all().count()
    
    def getActiveMemberCount():
        '''Gets all the active Member count'''
        activeMemberCount=0
        
        allMembers=Members.objects.all()

        for i in allMembers:
            if(MDT_DATA.get_member_account_status(i.ieee_id)):
                activeMemberCount+=1

        return activeMemberCount
    
    def getEventCount():
        '''Gets all the event Count'''
        return Events.objects.all().count()

    def get_event_for_calender():

        '''This function returns the events to show them on calender'''
        
        try:
            all_events = HomepageItems.load_all_events(True)
            date_and_events = {}
            for event in all_events:
                try:
                    date = event.event_date.strftime("%Y-%m-%d")
                except:
                    date = ""

                if date in date_and_events:
                    date_and_events[date].append(event)
                else:
                    date_and_events[date] = [event]

            return date_and_events
        except:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def get_upcoming_event():
        
        try:
            current_datetime = timezone.now()
            upcoming_event = Events.objects.filter(publish_in_main_web = True,event_date__gt=current_datetime).order_by('event_date')[:1]
            return upcoming_event[0]
        except:
            return None 
    
    def get_upcoming_event_banner_picture(event):

        try:
            return Graphics_Banner_Image.objects.get(event_id = event)
        except:
            return None
    
    def get_ip_address(request):
        
        address = request.META.get('HTTP_X_FORWARDED_FOR')
        print(address)
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        user =User_IP_Address(ip_address = ip)
        print(datetime.today())
        print(f"Current user ip address {user}")
        result = User_IP_Address.objects.filter(ip_address = ip,created_at = datetime.today())
        print(f"User exists in database {result}")
        if len(result)>=1:
            pass
        else:
            user.save()

    

        
