from django.shortcuts import render,redirect
from system_administration.models import Project_leads,Project_Developers
from django.conf import settings


# Create your views here.
def homepage(request):
    #check if user is already logged in
    user=request.user
    if (user.is_authenticated):
        return redirect('users:dashboard')
    else:
        return render(request,'port/landing_page.html')

def developed_by(request):
    '''This function loads and shows all the developers for the site'''
    #load leads and the developers of the project
    project_leads=Project_leads.objects.all()
    project_developers=Project_Developers.objects.all().order_by('-reputation_point')
    print(settings.MEDIA_URL)
    print(project_developers[0].developers_picture)
    
    context={
        'project_leads':project_leads,
        'project_developers':project_developers,
        'media':settings.MEDIA_URL
    }
    return render(request,'port/developer_intro.html',context)