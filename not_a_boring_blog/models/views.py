from django.db import models
from .user import User
from .post import Post


class View(models.Model):
    """View model - registers views on posts"""
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)