
##THIS .py FILE TESTS THE RELATED MODEL, VIEWS, URLS, Functions

from django.test import SimpleTestCase,TestCase,Client
from django.shortcuts import render,redirect
from django.urls import reverse,resolve
from port.views import homepage
import json

# class TestUrls(SimpleTestCase):
#     def test_homepage_url(self):
#         url=reverse('port:homepage')
#         self.assertEquals(resolve(url).func,homepage)


        