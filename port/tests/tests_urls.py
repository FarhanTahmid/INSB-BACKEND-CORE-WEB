
##THIS .py FILE TESTS IF ALL THE URLS ARE WORKING ON PORT APP

from django.test import SimpleTestCase
from django.urls import reverse,resolve
from port.views import homepage


class TestUrls(SimpleTestCase):
    def test_homepage_url(self):
        url=reverse('port:homepage')
        self.assertEquals(resolve(url).func,homepage)