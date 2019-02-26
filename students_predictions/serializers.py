from students_predictions.models import StudentSurvey
from rest_framework import serializers

class StudentSurveySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StudentSurvey
        fields = ('id', 'year', 'age', 'result')
