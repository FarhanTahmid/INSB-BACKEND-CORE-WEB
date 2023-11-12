from django.shortcuts import render

# Create your views here.

def main_website_update_view(request):
    return render(request,'main_web_update_view.html')