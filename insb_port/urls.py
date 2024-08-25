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
from django.urls import path,include,re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    
    path('',include('main_website.urls',namespace='main_website')),
    path('portal/',include('port.urls',namespace='port')),
    path('api/',include('api.urls')),
    path('admin/', admin.site.urls),
    path('system/',include('system_administration.urls',namespace="system")),
    path('portal/users/',include('users.urls',namespace="users")),
    path('portal/notifications/',include('notification.urls',namespace="notification")),
    path('portal/recruitment/',include('recruitment.urls',namespace="recruitment")),
    path('portal/central_branch/',include('central_branch.urls',namespace='central_branch')),
    path('portal/membership_development_team/',include('membership_development_team.urls',namespace='membership_development_team')),
    path('portal/public_relation_team/',include('public_relation_team.urls',namespace='public_relation_team')),
    path('portal/system_administration',include('system_administration.urls',namespace='system_administration')),
    path('portal/events_and_management_team/',include('events_and_management_team.urls',namespace="events_and_management_team")),
    path('portal/logistics_and_operations_team/',include('logistics_and_operations_team.urls',namespace="logistics_and_operations_team")),
    path('portal/content_writing_and_publications_team/',include('content_writing_and_publications_team.urls',namespace="content_writing_and_publications_team")),
    path('portal/promotions_team/',include('promotions_team.urls',namespace="promotions_team")),
    path('portal/website_development_team/',include('website_development_team.urls',namespace='website_development_team')),
    path('portal/media_team/',include('media_team.urls',namespace='media_team')),
    path('portal/graphics_team/',include('graphics_team.urls',namespace="graphics_team")),
    path('portal/finance_and_corporate_team/',include("finance_and_corporate_team.urls",namespace="finanace_and_corporate_team")),
    path('portal/SC_AG/',include("chapters_and_affinity_group.urls",namespace="sc_ag")),
    re_path(r'^media_files/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# handler404 = 'main_website.views.custom_404'


