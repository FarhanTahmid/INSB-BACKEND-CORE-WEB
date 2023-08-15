from .models import HomepageBannerPictureWithText
from django.http import HttpResponseServerError

class HomepageItems:
    
    def getHomepageBannerItems():
        try:
            return HomepageBannerPictureWithText.objects.all()
        except Exception as e:
            print(e)
            response = HttpResponseServerError("Oops! Something went wrong.")
            return response