from system_administration.render_access import Access_Render
from system_administration.models import Branch_Data_Access
from django.contrib import messages
import logging


class Branch_View_Access:

    def common_access(username):
        '''This function renders the common access of Faculties, EBS, Super & Staff users'''
    
        super_user_access=False
        staff_user_access=False
        eb_access=False

        # first check if the user is super user
        if(Access_Render.system_administrator_superuser_access(username=username)):
            super_user_access= True
        # first check if the user is staff user
        if(Access_Render.system_administrator_staffuser_access(username=username)):
            staff_user_access= True
        if(Access_Render.eb_access(username=username)):
            eb_access= True
        
        if(super_user_access or staff_user_access or eb_access):
            return True
        else:
            return False
    
    def get_create_event_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,create_event_access=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False
        
    def get_event_edit_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,event_details_page_access=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False

    def get_create_panel_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,create_panels_access=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False

    def get_team_details_view_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,team_details_page=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False


    