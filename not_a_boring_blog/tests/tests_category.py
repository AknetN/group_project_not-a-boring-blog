from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models.post import Category, Post
from django.contrib.auth.models import User
from ..serializers.posts import PostSerializer
from ..permissions import IsAdminRole, IsModeratorRole
from django.urls import reverse
from rest_framework.authtoken.models import Token
from ..models.user import Role
import json


class CreateCategoryTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create(username='user', password='passworduser')

        self.admin = User.objects.create(username="admin", password="passwordadmin")
        self.admin_token = Token.objects.create(user=self.admin)
        self.admin_role = Role.objects.create(user=self.admin, is_admin=True)
        
        self.blogger = User.objects.create(username="blogger", password="passwordblogger")
        self.blogger_token = Token.objects.create(user=self.blogger)
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        
        self.url = reverse('not_a_boring_blog:create_category') 
    
    
    def test_create_new_category_by_admin(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.admin_token}',
            'content_type': 'application/json',
            }
        data = {'category_name': 'TestCategory'}
        response = self.client.post(self.url, data=json.dumps(data), **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_existing_category_by_admin(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.admin_token}',
            'content_type': 'application/json',
            }
        data = {'category_name': 'TestCategory'}
        response = self.client.post(self.url, data=json.dumps(data), **headers)
        response1 = self.client.post(self.url, data=json.dumps(data), **headers)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
    
    
    def test_create_new_category_by_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token}',
            'content_type': 'application/json',
            }
        data = {'category_name': 'TestCategoryBlogger'}
        response = self.client.post(self.url, data=json.dumps(data), **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_existing_category_by_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token}',
            'content_type': 'application/json',
            }
        data = {'category_name': 'TestCategoryBlogger'}
        response = self.client.post(self.url, data=json.dumps(data), **headers)
        response1 = self.client.post(self.url, data=json.dumps(data), **headers)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
    
    
    def test_create_category_by_unregistered_user(self):
        response = self.client.post(self.url) 
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    


class ListCategoriesTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create(username='user', password='passworduser')

        self.admin = User.objects.create(username="admin", password="passwordadmin")
        self.admin_token = Token.objects.create(user=self.admin)
        self.admin_role = Role.objects.create(user=self.admin, is_admin=True)
        
        self.moderator = User.objects.create(username="moderator", password="passwordmoderator")
        self.moderator_token = Token.objects.create(user=self.moderator)
        self.moderator_role = Role.objects.create(user=self.moderator, is_moderator=True)
        
        self.blogger = User.objects.create(username="blogger", password="passwordblogger")
        self.blogger_token = Token.objects.create(user=self.blogger)
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        
        self.url = reverse('not_a_boring_blog:list_categories') 
        
        self.category1 = Category.objects.create(category_name='Category1')
        self.category2 = Category.objects.create(category_name='Category2')
    
    def test_list_categories_as_admin(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_categories = ['Category1', 'Category2']
        self.assertEqual(len(response.data), len(expected_categories))
        response_categories = [category['category_name'] for category in response.data]
        self.assertCountEqual(response_categories, expected_categories)


    def test_list_categories_as_unauthorized_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
