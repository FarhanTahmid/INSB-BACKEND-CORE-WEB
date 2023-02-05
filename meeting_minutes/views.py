from django.shortcuts import render

# Create your views here.
def team_meeting_minutes(request):
    return render(request,'team_meeting_minutes.html')


def branch_meeting_minutes(request):
    return render(request,'branch_meeting_minutes.html')
