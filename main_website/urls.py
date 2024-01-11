from django.urls import path
from . import views

app_name = "main_website"

urlpatterns = [
    path('',views.homepage,name="homepage"),
    
    #ACTIVITY URLS
    # Event
    path('events/',views.event_homepage,name="event_homepage"),
    path('events/<int:event_id>/', views.event_details, name="event_details"),
    
    #SOCIETY AG URLS
    path('ieee_nsu_ras_sbc/',views.rasPage,name="ras_home"),
    path('ieee_nsu_pes_sbc/',views.pesPage,name="pes_home"),
    path('ieee_nsu_ias_sbc/',views.iasPage,name="ias_home"),
    path('ieee_nsu_wie_sbc/',views.wiePage,name="wie_home"),
    path('events/<int:primary>',views.events_for_sc_ag,name="events_for_sc_ag"),

    #Achievements
    path('achievements/',views.achievements,name="achievements"),
    path('news/',views.news,name="news"),
    path('news/<int:pk>',views.news_description,name="news_description"),
    #Gallery
    path('gallery/',views.gallery,name="gallery"),
    
    # Members
    path('panels/',views.current_panel_members,name="panel_members"),
    path('panels/<str:year>',views.panel_members_page,name="panel_members_previous"),
    path('officers',views.officers_page,name="officer_page"),
    path('officers/<str:team_primary>',views.team_based_officers_page,name="team_officer"),
    path('volunteers',views.volunteers_page,name="volunteers_page"),
    path('exemplary_members',views.exemplary_members,name="exemplary_members"),
    path('all_members',views.all_members,name="all_members"),
    path('team/<int:team_primary>',views.team_intros,name="team_intro"),
    path('member_profile/<str:ieee_id>',views.member_profile, name="member_profile"),

    # Publications
    path('blogs',views.blogs,name="blogs"),
    path('blogs/<int:pk>',views.blog_description, name="blog_description"),
    path('write_blogs',views.write_blogs,name="write_blogs"),
    path('magazines',views.magazines,name="magazines"),
    path('research',views.research_Paper,name="research_paper"),
    path('add_research',views.add_research_form,name="add_research"),

    # About
    path('ieee_bangladesh_section',views.ieee_bd_section, name="ieee_bangladesh_section"),
    path('ieee_nsu_student_branch',views.ieee_nsu_student_branch, name="ieee_nsu_student_branch"),
    path('ieee_region_10',views.ieee_region_10, name="ieee_region_10"),
    path('ieee',views.ieee, name="ieee"),
    path('faq',views.faq, name="faq"),

    # Contact
    path('contact',views.contact, name="contact"),
    # Toolkit
    path('toolkit',views.toolkit, name="toolkit"),
    # Join INSB
    path('join_insb',views.join_insb, name = "join_insb"),
    
    # path('hello',views.test_view,name="404"),
]
