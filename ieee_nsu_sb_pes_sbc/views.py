from django.shortcuts import render

# Create your views here.

def pes_homepage(request):
    return render(request,'PES/homepage.html')

def pes_members(request):
    return render (request, 'pes_members/members.html')