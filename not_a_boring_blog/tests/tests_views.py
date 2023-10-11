from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from ..models.comment import Comment
from ..models.post import Post
from ..models.user import Role
from ..models.views import View
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from datetime import timedelta




class CreatePostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.blogger2 = User.objects.create(username='blogger2', password=make_password('bloggerpass2'))
        self.blogger_role2 = Role.objects.create(user=self.blogger2, is_blogger=True)
        self.blogger_token2 = Token.objects.create(user=self.blogger2) 

        self.post = Post.objects.create(
            title='Test post Post',
            body='Test post Body',
            user_id=self.blogger2,
            status='published',
            min_read='5',
            description='Test post Description'
        )
        self.url = reverse('not_a_boring_blog:create_post_view', kwargs={'post_id': self.post.id})


    def test_create_post_view_successful(self):
        """Test creating a post view successfully."""
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.post(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_create_post_view_author_own_view(self):
        """Test creating a view for the author's own post."""
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token2.key}',
            'content_type': 'application/json',
        }
        response = self.client.post(self.url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_create_post_view_cooldown_not_elapsed(self):
        """Test creating a view when the cooldown period has not elapsed."""
        View.objects.create(post_id=self.post, user_id=self.blogger)
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.post(self.url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


    def test_create_post_view_cooldown_elapsed(self):
        """Test creating a view when the cooldown period has elapsed."""
        last_view = View.objects.create(post_id=self.post, user_id=self.blogger)
        last_view.timestamp = now() - timedelta(minutes=6)  # Set timestamp to 6 minutes ago
        last_view.save()

        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.post(self.url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class GetPostViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.blogger2 = User.objects.create(username='blogger2', password=make_password('bloggerpass2'))
        self.blogger_role2 = Role.objects.create(user=self.blogger2, is_blogger=True)
        self.blogger_token2 = Token.objects.create(user=self.blogger2) 

        self.post = Post.objects.create(
            title='Test post Post',
            body='Test post Body',
            user_id=self.blogger2,
            status='published',
            min_read='5',
            description='Test post Description'
        )
        self.url = reverse('not_a_boring_blog:post_views', kwargs={'post_id': self.post.id})
    
    
    def test_get_post_views_with_no_views(self):
        """Test retrieving the view count for a post."""
        response = self.client.get(self.url)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_get_views_count_with_recorded_views(self):
        """Test retrieving the view count for a post with recorded views."""
        View.objects.create(post_id=self.post, user_id=self.blogger)
        View.objects.create(post_id=self.post, user_id=self.blogger2)

        response = self.client.get(self.url)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_post_views_post_not_found(self):
        """Test retrieving view count for a non-existent post."""

        non_existent_post_id = self.post.id + 100  # A non-existent post ID
        url = reverse('not_a_boring_blog:post_views', kwargs={'post_id': non_existent_post_id})
        
        response = self.client.get(url)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

