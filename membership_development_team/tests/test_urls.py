from django.test import SimpleTestCase
from django.urls import reverse,resolve
from membership_development_team.views import md_team_homepage,generateExcelSheet_membersList,insb_members_list,member_details,membership_renewal,renewal_session_data,membership_renewal_form,membership_renewal_form_success,getRenewalStats
from membership_development_team.views import renewal_request_details,generateExcelSheet_renewal_requestList,data_access,site_registration_request_home,site_registration_form,confirmation_of_form_submission,site_registration_request_details,getSiteRegistrationRequestStats
#Tesing urls for this application

class TestUrls(SimpleTestCase):

    def test_md_team_homepage_resolves(self):
        url = reverse('membership_development_team:md_team_homepage')
        self.assertEquals(resolve(url).func,md_team_homepage)
    
    def test_insb_members_list_resolves(self):
        url = reverse('membership_development_team:members_list')
        self.assertEquals(resolve(url).func,insb_members_list)
    
    def test_member_details_resolves(self):
        url = reverse('membership_development_team:member_details',args=[1])#any number
        self.assertEquals(resolve(url).func,member_details)
    
    def test_export_excel_resolves(self):
        url = reverse('membership_development_team:export_excel')
        self.assertEquals(resolve(url).func,generateExcelSheet_membersList)

    def test_membership_renewal_resolves(self):
        url = reverse('membership_development_team:membership_renewal')
        self.assertEquals(resolve(url).func,membership_renewal)

    def test_renewal_session_data_resolves(self):
        url = reverse('membership_development_team:renewal_session_data',args=['some-string'])
        self.assertEquals(resolve(url).func,renewal_session_data)
    
    def test_membership_renewal_form_resolves(self):
        url = reverse('membership_development_team:renewal_form',args=['some-string'])
        self.assertEquals(resolve(url).func,membership_renewal_form)
    
    def test_membership_renewal_form_resolves(self):
        url = reverse('membership_development_team:renewal_form',args=['some-string'])
        self.assertEquals(resolve(url).func,membership_renewal_form)

    def test_membership_renewal_form_success_resolves(self):
        url = reverse('membership_development_team:renewal_form_success',args=['some-string'])
        self.assertEquals(resolve(url).func,membership_renewal_form_success)

    def test_request_details_resolves(self):
        url = reverse('membership_development_team:request_details',args=['some-string','some-string'])
        self.assertEquals(resolve(url).func,renewal_request_details)
    
    def test_export_excel_renewal_request_resolves(self):
        url = reverse('membership_development_team:export_excel_renewal_request',args=['some-string'])
        self.assertEquals(resolve(url).func,generateExcelSheet_renewal_requestList)
    
    def test_renewal_stats_resolves(self):
        url = reverse('membership_development_team:renewal_stats')
        self.assertEquals(resolve(url).func,getRenewalStats)

    def test_data_access_resolves(self):
        url = reverse('membership_development_team:data_access')
        self.assertEquals(resolve(url).func,data_access)
    
    def test_site_registration_resolves(self):
        url = reverse('membership_development_team:site_registration')
        self.assertEquals(resolve(url).func,site_registration_request_home)

    def test_site_registration_form_resolves(self):
        url = reverse('membership_development_team:site_registration_form')
        self.assertEquals(resolve(url).func,site_registration_form)

    def test_confirmation_resolves(self):
        url = reverse('membership_development_team:confirmation')
        self.assertEquals(resolve(url).func,confirmation_of_form_submission)

    def test_site_registration_request_details_resolves(self):
        url = reverse('membership_development_team:site_registration_request_details',args=[5])#some number
        self.assertEquals(resolve(url).func,site_registration_request_details)

    def test_site_registration_stats_resolves(self):
        url = reverse('membership_development_team:site_registration_stats')
        self.assertEquals(resolve(url).func,getSiteRegistrationRequestStats)