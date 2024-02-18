from django.shortcuts import render

# Create your views here.
def task_homepage(request):
        return render(request,"task_homepage.html")