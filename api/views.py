from django.shortcuts import render
from users.models import Members
from api.serializers import MembersSerializer
from rest_framework.generics import ListAPIView
# Create your views here.
#Creating the api view for Members here
class MemberList(ListAPIView):
    queryset=Members.objects.all()
    serializer_class=MembersSerializer