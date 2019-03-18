# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class StudentSurvey(models.Model):
    class Meta:
      db_table = 'students_surveys'

    ci = models.CharField(max_length=255)
    year = models.IntegerField()
    age = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    education = models.CharField(max_length=255)
    works = models.CharField(max_length=255)
    works_related = models.CharField(max_length=255)
    semester_subjects_count = models.IntegerField()
    course_take_count = models.CharField(max_length=255)
    assists_theoretical = models.CharField(max_length=255)
    assists_practical = models.CharField(max_length=255)
    study_method = models.CharField(max_length=255)
    study_hours = models.CharField(max_length=255)
    motivation_level = models.CharField(max_length=255)
    result = models.CharField(max_length=255)

class CourseResult(models.Model):
    ci = models.CharField(max_length=255)
    year = models.IntegerField()
    name = models.CharField(max_length=255)
    test1 = models.CharField(max_length=255)
    test2 = models.CharField(max_length=255)
    final = models.CharField(max_length=255)
    assignment1 = models.CharField(max_length=255)
    assignment2 = models.CharField(max_length=255)
    assignment3 = models.CharField(max_length=255)
    assignment4 = models.CharField(max_length=255)
    assignment5 = models.CharField(max_length=255)
