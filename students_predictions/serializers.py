from django.contrib.auth.models import User, Group
from rest_framework import serializers

class StudentSurveySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')
