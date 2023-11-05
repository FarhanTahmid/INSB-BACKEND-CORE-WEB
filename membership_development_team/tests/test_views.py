from django.test import TestCase,Client,RequestFactory
from django.urls import reverse
from users.models import Members
from port.models import Teams,Roles_and_Position
from django.contrib.auth.models import User
from membership_development_team.models import Renewal_Sessions,Renewal_requests,Renewal_Form_Info,Portal_Joining_Requests
import json

class TestViews(TestCase):

    def setUp(self):
        
        self.client = Client()
        self.md_team_homepage_url = reverse('membership_development_team:md_team_homepage')
        self.insb_member_list_url = reverse('membership_development_team:members_list')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')


        
        
    
    def test_md_team_homepage_GET(self):
        team = Teams.objects.create(primary=7,team_name="Membership Development")
        roles = [Roles_and_Position.objects.create(role="Core-volunteer",pk=0),Roles_and_Position.objects.create(role="Volunteer",pk=1)]
        response = self.client.get(self.md_team_homepage_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'md_team_homepage.html')


        self.assertIn('co_ordinators', response.context)
        self.assertIn('incharges', response.context)
        self.assertIn('core_volunteers', response.context)
        self.assertIn('volunteers', response.context)
        self.assertIn('media_url', response.context)
        self.assertIn('user_data', response.context)

    def test_md_team_insb_member_list_POST(self):

        response = self.client.post(self.insb_member_list_url)
        self.assertEqual(response.status_code,302)
    
    def test_md_team_insb_member_list_GET(self):

        response = self.client.get(self.insb_member_list_url)
        self.assertEqual(response.status_code,200)



    


       

