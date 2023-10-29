from typing import Any
from system_administration.models import system
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from . urls import urlpatterns,app_name

class BlockMainWebMiddleWare:
    '''This class is basically designed to make the main website go down and show message of its updating'''
    def __init__(self,get_response):
        self.get_response=get_response
        
    def __call__(self,request):
        try:
            # first get from the system model that if the 'main_website_under_maintenance' is true
            get_system=system.objects.filter(main_website_under_maintenance=True).all()
            if get_system:
                for i in urlpatterns:
                    # get the url patterns of main website
                    pattern=str(i.pattern)
                    # check if the current url matches with main website. if matches block all the URLs and show the Updating page.
                    if (request.path[1:]==pattern):
                        return redirect('system_administration:main_web_update')
                
        except:
            print("All okay")
        response=self.get_response(request)
        return response