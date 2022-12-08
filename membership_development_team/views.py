from django.shortcuts import render
from users.models import Members
from port.models import Roles_and_Position
from recruitment import renderData


# Create your views here.
def md_team_homepage(request):
    return render(request,'md_team_homepage.html')

def members_list(request):
    '''This function is responsible to display all the member data in the page'''
    members=Members.objects.order_by('position')
    totalNumber=Members.objects.all().count()
    context={'members':members,'totalNumber':totalNumber}
          
    return render(request,'insb_member_list.html',context=context)