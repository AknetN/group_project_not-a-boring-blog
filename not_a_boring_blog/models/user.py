from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    """Role model - defines user roles on the blog"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_moderator = models.BooleanField(default=False)
    is_blogger = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    bio = models.CharField(max_length=500)

    def __str__(self):
        return self.user.username
