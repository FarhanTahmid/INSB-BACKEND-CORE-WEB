from django.shortcuts import render

# Create your views here.
def task_homepage(request):
        return render(request,"task_homepage.html")
def task_home(request):
        return render(request,"task_home.html")