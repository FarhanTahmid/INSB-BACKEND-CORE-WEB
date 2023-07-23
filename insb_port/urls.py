"""insb_port URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',include('port.urls',namespace='port')),
    path('api/',include('api.urls')),
    path('admin/', admin.site.urls),
    path('users/',include('users.urls',namespace="users")),
    path('recruitment/',include('recruitment.urls',namespace="recruitment")),
    path('central_branch/',include('central_branch.urls',namespace='central_branch')),
    path('membership_development_team/',include('membership_development_team.urls',namespace='membership_development_team')),
    path('public_relation_team/',include('public_relation_team.urls',namespace='public_relation_team')),
    path('system_administration',include('system_administration.urls',namespace='system_administration')),
    path('main_website/',include('main_website.urls',namespace='main_website')),
    path('events_and_management_team/',include('events_and_management_team.urls',namespace="events_and_management_team.urls"))
    
]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)