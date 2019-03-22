# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Student(models.Model):
    ci = models.CharField(max_length=255)
    course_detail_id = models.IntegerField()
    name = models.CharField(max_length=255)
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
    test1 = models.CharField(max_length=255)
    test2 = models.CharField(max_length=255)
    final = models.CharField(max_length=255)
    assignment1 = models.CharField(max_length=255)
    assignment2 = models.CharField(max_length=255)
    assignment3 = models.CharField(max_length=255)
    assignment4 = models.CharField(max_length=255)
    assignment5 = models.CharField(max_length=255)
    access_count = models.IntegerField()
    forum_activity = models.IntegerField()
    survey_response_count = models.IntegerField()
    file_access_count = models.IntegerField()
    result = models.CharField(max_length=255)

class Prediction(models.Model):
    class Meta:
        db_table = 'predictions'
    CourseDetailId = models.IntegerField()
    Result = models.CharField(max_length=255)
    Timestamp = models.DateTimeField()
