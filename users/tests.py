from django.test import SimpleTestCase
from django.urls import reverse,resolve
from users.views import login,signup,dashboard,logoutUser,profile_page,forgotPassword_getUsername,invalidURL

class userURLTests(SimpleTestCase):
    
    def test_login_page(self):
        url=reverse('users:login')
        self.assertEquals(resolve(url).func,login)
    
    def test_signup_page(self):
        url=reverse('users:signup')
        self.assertEquals(resolve(url).func,signup)
    
    def test_dashboard(self):
        url=reverse('users:dashboard')
        self.assertEquals(resolve(url).func,dashboard)
    
    def test_logout(self):
        url=reverse('users:logoutUser')
        self.assertEqual(resolve(url).func,logoutUser)
    
    def test_profile_page(self):
        url=reverse('users:profile')
        self.assertEqual(resolve(url).func,profile_page)
    
    def test_forgot_pass_validation(self):
        url=reverse('users:fp_validation')
        self.assertEqual(resolve(url).func,forgotPassword_getUsername)
        
    def test_invalid_url(self):
        url=reverse('users:invalid_url')
        self.assertEqual(resolve(url).func,invalidURL)
    