# The above code defines two Django models, Category and Post, with various fields and relationships.
from django.db import models
from .user import Role
from django.contrib.auth.models import User

class Category(models.Model):
    """Category model"""
    category_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.category_name


class Post(models.Model):
    """Post model"""
    STATUS = [
        ('published', 'Published'),
        ('private', 'Private'),
        ('editing', 'Editing'),
    ]
    category = models.ManyToManyField(Category, related_name='posts') # on_delete=models.CASCADE is not applied in ManyToMany
    title = models.CharField(max_length=255)
    body = models.TextField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=20, choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True) # the field will be automatically set to the current timestamp when a new object is created. It will not change when the object is updated in the future.
    last_updated = models.DateTimeField(auto_now=True) # the field will be automatically updated to the current timestamp every time the object is saved (updated), regardless of whether it's a new object or an existing one
    min_read = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    class Meta:
        ordering = ['-last_updated', '-created_at']

    def __str__(self):
        return self.title
    
    def update_categories(self, categories):
        post_categories = self.category.all()
        list_categories = [category.id for category in post_categories]
        
        for category in post_categories:
            if category.id not in categories:
                self.category.remove(category)
        
        for category in categories:
            if category not in list_categories:
                self.category.add(category)
