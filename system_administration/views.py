from django.shortcuts import render,redirect
from .render_access import Access_Render
from .models import system

# Create your views here.

def main_website_update_view(request):
    if(Access_Render.system_administrator_superuser_access(request.user.username) or Access_Render.system_administrator_staffuser_access(request.user.username)):
        return redirect('main_website:homepage')
    if(system.objects.filter(main_website_under_maintenance=False).first()):
        return redirect('main_website:homepage')
    else:    
        return render(request,'main_web_update_view.html')