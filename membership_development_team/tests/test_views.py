from django.test import TestCase,Client
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
        Teams.objects.create(team_name="Membership Development",primary=7)
        Members.objects.create(ieee_id=1, name='Co-ordinator 1',nsu_id=1234, position=Roles_and_Position.objects.create(role="Co-ordinator",pk=9))
        
    
    def test_md_team_homepage_GET(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.md_team_homepage_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'md_team_homepage.html')

        #Checking only one as the rest would be same
        self.assertIn('co_ordinators', response.context)
       

    def test_md_team_insb_member_list_authenticated(self):

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.insb_member_list_url)
        
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'INSB Members/members_list.html')

        self.assertIn('members',response.context)
        self.assertIn('totalNumber', response.context)
        self.assertIn('has_view_permission', response.context)
        self.assertIn('user_data', response.context)

        self.assertContains(response, 'Co-ordinator 1')

    def test_md_team_insb_member_list_unauthenticated(self):
        self.client.logout()
        response = self.client.post(self.insb_member_list_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/portal/users/login?next=/portal/membership_development_team/members/')
    
    
    
        



    


       

