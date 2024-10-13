import imp
from django.urls import path,include
from . import views
from .views import GetTaskCategoryPointsAjax, SaveMemberTaskPointsAjax, UpdatePositionAjax,UpdateAwardAjax
from .views import UpdatePositionAjax,UpdateRestrictionAjax,AwardRanking

app_name='central_branch'

##defining the urls to work with

urlpatterns = [
    
    #central_homeage
    path('',views.central_home, name='central_home'),
    #teams page
    path('teams/',views.teams,name='teams'),
    #team details page
    path('team_details/<int:primary>/<str:name>',views.team_details,name='team_details'),
    #manage team Page
    path('manage_team/<str:pk>/<str:team_name>',views.manage_team,name="manage_team"),

    #PANEL
    path('panels',views.panel_home,name="panels"),
    #panel details
    path('panels/<int:panel_id>',views.branch_panel_details,name="panel_details"),
    path('panels/<int:panel_id>/officers',views.branch_panel_officers_tab,name="panel_details_officers"),
    path('panels/<int:panel_id>/volunteers',views.branch_panel_volunteers_tab,name="panel_details_volunteers"),
    path('panels/<int:panel_id>/alumni',views.branch_panel_alumni_tab,name="panel_details_alumni"),

    
    #for updating value in team member select box in event assigning
    # path('get_updated_options/', views.get_updated_options_for_event_dashboard, name='get_updated_options'),
    #others page
    path('others/',views.others,name="others"),
    
    
    #WEBSITE Management URL Path
    path('manage_website/homepage',views.manage_website_homepage,name="manage_website_home"),
    path('manage_website/homepage/update/<int:pk>',views.manage_website_homepage_top_banner_update,name="manage_website_home_top_banner_update"),
    # path('manage_website/homepage/volunteer_of_the_month/<int:pk>',views.update_volunteer_of_month,name="update_vom"),
    path('manage_website/achievements',views.manage_achievements,name="manage_achievements"),
    path('manage_website/achievements/update/<int:pk>',views.update_achievements,name="achievements_update"),
    path('manage_website/news',views.manage_news,name="manage_news"),
    path('manage_website/news/update/<int:pk>',views.update_news,name="update_news"),
    path('manage_website/blogs',views.manage_blogs,name="manage_blogs"),
    path('manage_website/blogs/update/<int:pk>',views.update_blogs,name="update_blogs"),
    path('manage_website/blogs/requests',views.blog_requests,name="blog_requests"),
    path('manage_website/blogs/requests/<int:pk>',views.publish_blog_request,name="publish_blog_requests"),
    path('manage_website/research',views.manage_research,name="manage_research"),
    path('manage_website/research/update/<int:pk>',views.update_researches,name="update_researches"),
    path('manage_website/research/requests',views.manage_research_request,name="manage_research_request"),
    path('manage_website/research/requests/<int:pk>',views.publish_research_request,name="publish_research_request"),
    path('manage_website/magazine',views.manage_magazines,name="manage_magazines"),
    path('manage_website/magazine/update/<int:pk>',views.update_magazine,name="update_magazine"),
    path('manage_website/gallery',views.manage_gallery,name="manage_gallery"),
    path('manage_website/gallery/update/image/<int:pk>',views.update_images,name="update_image"),
    path('manage_website/gallery/update/video/<int:pk>',views.update_videos,name="update_video"),
    path('manage_website/exemplary_members',views.manage_exemplary_members,name="manage_exemplary_members"),
    path('manage_website/exemplary_members/update/<int:pk>',views.update_exemplary_members,name="update_exemplary_members"),
    path('manage_website/about/ieee/',views.manage_about,name = "manage_about"),
    path('manage_website/about/ieee_region_10/',views.ieee_region_10,name = "ieee_region_10"),
    path('manage_website/about/ieee_bangladesh_section/',views.ieee_bangladesh_section,name = "ieee_bangladesh_section"),
    path('manage_website/about/ieee_nsu_student_branch/',views.ieee_nsu_student_branch,name = "ieee_nsu_student_branch"),
    path('manage_website/about/faq/',views.faq,name = "faq"),
    path('manage_website/toolkit',views.manage_toolkit,name="manage_toolkit"),
    path('manage_website/toolkit/update/<int:pk>',views.update_toolkit,name="update_toolkit"),
    path('manage_website/feedbacks',views.feedbacks,name="feedbacks"),
    path('manage_access',views.manage_view_access,name="manage_access"),
    
    #About Page preview urls
    path('manage_website/about/ieee/preview/',views.manage_about_preview,name = "manage_about_preview"),
    path('manage_website/about/ieee_region_10/preview/',views.ieee_region_10_preview,name = "ieee_region_10_preview"),
    path('manage_website/about/ieee_bangladesh_section/preview/',views.ieee_bangladesh_section_preview,name = "ieee_bangladesh_section_preview"),
    path('manage_website/about/ieee_nsu_student_branch/preview/',views.ieee_nsu_student_branch_preview,name = "ieee_nsu_student_branch_preview"),
    path('manage_website/about/faq/preview',views.faq_preview,name = "faq_preview"),

    #Events urls
    #Event control page 
    path('events/',views.event_control_homepage, name='event_control'),
    #Event Creation Form page 1
    path('events/create_event/',views.event_creation_form_page,name='event_creation_form1'),
    #Event Creation Form Page 2
    path("events/create_event/<int:event_id>/page-2/", views.event_creation_form_page2, name="event_creation_form2"),
    #Event creation page 3
    path("events/create_event/<int:event_id>/page-3/", views.event_creation_form_page3, name="event_creation_form3"),
    #Event edit page
    path('event_details/<int:event_id>/edit/',views.event_edit_form,name='event_edit_form'),
    #Event media tab page
    path('event_details/<int:event_id>/edit/media/',views.event_edit_media_form_tab,name='event_edit_media_form_tab'),
    #Event graphics tab page
    path('event_details/<int:event_id>/edit/graphics/',views.event_edit_graphics_form_tab,name='event_edit_graphics_form_tab'),
    #Event graphics links sub tab page
    path('event_details/<int:event_id>/edit/graphics/links/',views.event_edit_graphics_form_links_sub_tab,name='event_edit_graphics_form_links_sub_tab'),
    #Event content tab page
    path('event_details/<int:event_id>/edit/content/',views.event_edit_content_form_tab,name='event_edit_content_form_tab'),
    #Mega Event Creation Form
    path('events/create_mega_event/',views.mega_event_creation,name="mega_event_creation"), 
    #Mega Events homepage
    path('events/mega_events/',views.mega_events,name="mega_events"), 
    #Mega Events edit
    path('events/mega_event_edit/<int:mega_event_id>/',views.mega_event_edit,name="mega_event_edit"), 
    #Add Events to Mega Event
    path('events/mega_event_add_event/<int:mega_event_id>/',views.mega_event_add_event,name="mega_event_add_event"), 

    #Event preview
    path('event_details/<int:event_id>/preview/',views.event_preview,name='event_preview'),
    #Event Feedback
    path('event_details/<int:event_id>/feedbacks/',views.event_feedback,name="event_feedback"),  

    #Event Google Calendar
    path('event_details/<int:event_id>/google_calendar/',views.event_google_calendar,name="google_calendar"),  

    #Members list
    path('members/',views.insb_members_list,name="members_list"),
    #Members details list
    path('member_details/<int:ieee_id>',views.member_details,name="member_details"),

    # get dynamic data in JS position edit
    path('get_position_data/',UpdatePositionAjax.as_view(),name="update_position"),
    #evente excel generation url
    path('generateExcelSheet_events_by_year/<int:year>',views.generateExcelSheet_events_by_year,name="generateExcelSheet_events_by_year"),
    
    # volunteer awards
    path('volunteer_awards/panels/',views.volunteerAwardsPanel,name="volunteer_awards_panels"),
    path('volunteer_awards/panel/<int:panel_pk>/awards',views.panel_specific_volunteer_awards_page,name="panel_specific_volunteer_awards_page"),
    path('volunteer_awards/panel/<int:panel_pk>/awards/<int:award_pk>',views.panel_and_award_specific_page,name="panel_award_specific_volunteer_awards_page"),
    path('get_award_data/',UpdateAwardAjax.as_view(),name="update_award"),
    path('rank_award/',AwardRanking.as_view(),name="award_ranking"),
    #event excel generation url
    path('generateExcelSheet_events_by_year/<int:year>',views.generateExcelSheet_events_by_year,name="generateExcelSheet_events_by_year"),
    path('members/user_access/',views.user_access,name="user_access"),
    path('update_restricted_members/',UpdateRestrictionAjax.as_view(),name="update_restricted_members"),

    #task assignation urls
    path('create_task/',views.create_task,name="create_task"),
    path('task_home/',views.task_home,name="task_home"),
    path('task/<int:task_id>',views.task_edit,name="task_edit"),
    path('task/<int:task_id>/upload_task/',views.upload_task,name="upload_task"),
    path('task/<int:task_id>/forward_to_incharges/<int:team_primary>',views.forward_to_incharges,name="forward_to_incharges"),
    path('task/<int:task_id>/add_task/',views.add_task,name="add_task"),
    path('task/get_task_category_points',GetTaskCategoryPointsAjax.as_view(),name="get_task_category_points"),
    path('task/save_mem_task_points/<team_primary>/',SaveMemberTaskPointsAjax.as_view(),name="save_mem_task_points"),

    #task history
    path('task_history/individual/<int:ieee_id>',views.individual_task_history,name="individual_task_history"),
    path('task_history/team/<int:team_primary>',views.team_task_history,name="team_task_history"),
    ##
    path('task_leaderboard/',views.task_leaderboard,name="task_leaderboard"),

    #Email
    path('mail/',views.mail,name="mail"),
    path('mail/view/<str:mail_id>',views.view_mail,name="view_mail"),
    path('mail/send_mail_request/', views.SendMailAjax.as_view(),name='send_mail_request'),
    path('mail/send_reply_mail_request/',views.SendReplyMailAjax.as_view(),name='send_reply_mail_request'),
    path('mail/send_forward_mail_request/',views.SendForwardMailAjax.as_view(),name='send_forward_mail_request'),
    path('mail/request_read_unread/', views.ReadUnreadEmailAjax.as_view(),name='request_email_read_unread'),
    path('mail/request_delete/',views.DeleteEmailAjax.as_view(),name='request_email_delete'),
    path('mail/request_star_unstar/',views.StarUnstarEmailAjax.as_view(),name='request_email_star_unstar'),
    path('mail/request_scheduled/',views.GetScheduledEmailInfoAjax.as_view(),name='request_scheduled_email'),
    path('mail/request_update_schedule/',views.UpdateScheduledEmailOptionsAjax.as_view(),name='request_update_email_schedule'),
    path('navigate/', views.PaginationAjax.as_view(),name='navigate'),
    path('mail/view/attachments/<str:message_id>/<str:attachment_id>/', views.get_attachment, name='get_attachment'),
]