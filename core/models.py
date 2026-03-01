from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class LearningResource(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()

    url = models.URLField(max_length=500, blank=True, null=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    upload_time = models.DateTimeField(auto_now_add=True)

    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
