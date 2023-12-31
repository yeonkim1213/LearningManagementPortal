from django.db import models
from django.contrib.auth.models import User, Group

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    weight = models.PositiveIntegerField() 
    points = models.PositiveIntegerField() 
    

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    grader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='graded_set')
    file = models.FileField(upload_to='submissions/') 
    score = models.FloatField(null=True, blank=True, default=None)
