from rest_framework import serializers
from users.models import Members  #here we imported the model from users which is member(Generalized members who registered for INSB)

class MembersSerializer(serializers.ModelSerializer):
    class Meta:
        model=Members
        fields=[
            'ieee_id',
            'name',
            'email_ieee',
        ]