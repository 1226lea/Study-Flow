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

# Model for users to save/bookmark resources
class SavedResource(models.Model):
    # The user who saved the resource
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    
    # The specific resource that was saved (linked to YaQi's model)
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name='saved_by_users')
    
    # Timestamp for when the resource was saved
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Crucial: Prevents a user from saving the exact same resource multiple times
        unique_together = ('user', 'resource')

    def __str__(self):
        return f"{self.user.username} saved {self.resource.title}"