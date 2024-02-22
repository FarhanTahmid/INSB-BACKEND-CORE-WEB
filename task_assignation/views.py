from django.shortcuts import render

# Create your views here.
def create_task(request):
        return render(request,"create_task.html")
def task_home(request):
        return render(request,"task_home.html")
def upload_task(request):
        return render(request,"task_page.html")
def add_task(request):
        return render(request,"task_forword_to_members.html")
