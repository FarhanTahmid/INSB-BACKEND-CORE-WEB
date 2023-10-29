from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def pes_homepage(request):
    return render(request,'PES/homepage.html')

@login_required
def pes_members(request):
    
    return render (request, 'pes_members/members.html')