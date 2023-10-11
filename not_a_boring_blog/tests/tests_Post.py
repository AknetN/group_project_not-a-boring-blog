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

class PostListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.admin = User.objects.create(username='aknet1', password='Dci1234!')
        self.admin_token = Token.objects.create(user=self.admin)
        self.role = Role.objects.create(user=self.admin, is_admin=True, is_moderator=True)
        
        self.category = Category.objects.create(category_name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            body='Test Body',
            user_id=self.admin,
            status='published',
            min_read='5 mins',
            description='Test Description',
        )
        self.post.category.add(self.category)

    def test_list_admin(self):
        headers = {
                    'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
                    'content_type': 'application/json',
                }
        url = reverse('not_a_boring_blog:post-list')
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = PostSerializer(instance=[self.post], many=True).data
        self.assertEqual(response.data, expected_data)
    
    def test_list_unauthorized(self):
        url = reverse('not_a_boring_blog:post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class PostDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', password='testpassword')
        
        self.admin = User.objects.create(username='testuser2', password='testpassword2')
        self.admin_role = Role.objects.create(user=self.admin, is_admin=True)
        self.admin_token = Token.objects.create(user=self.admin)

        self.moderator = User.objects.create(username='moderator', password='testpassword3')
        self.moderator_role = Role.objects.create(user=self.moderator, is_moderator=True)
        self.moderator_token = Token.objects.create(user=self.moderator)
        
        self.blogger = User.objects.create(username='blogger', password='blogger')
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)
        
        self.blogger2 = User.objects.create(username='blogger2', password='blogger2')
        self.blogger_role2 = Role.objects.create(user=self.blogger2, is_blogger=True)
        self.blogger_token2 = Token.objects.create(user=self.blogger2)
        
        self.role = Role.objects.create(user=self.user, is_admin=True, is_moderator=True, is_blogger=True)
        self.category = Category.objects.create(category_name='Test Category')
        self.post = Post.objects.create(
            title='Test Post moderator',
            body='Test Body',
            user_id=self.moderator,
            status='published',
            min_read='5 mins',
            description='Test Description'
        )
        self.post.category.add(self.category)
        self.post2 = Post.objects.create(
            title='Test Post2 blogger',
            body='Test Body2',
            user_id=self.blogger,
            status='published',
            min_read='5 mins',
            description='Test Description2'
        )
        self.post2.category.add(self.category)
        self.url = reverse('not_a_boring_blog:post-detail', kwargs={'pk':self.post2.pk}) 
        
    def test_get_allow_all(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = PostSerializer(instance=self.post2).data
        self.assertEqual(response.data, expected_data)
    
    def test_put_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        body = {
            'title': 'Updated title from blogger',
            'body': self.post2.body,
            'user_id': self.post2.user_id_id,
            'status': self.post2.status,
            'min_read': self.post2.min_read,
            'description': 'Test Description2+',
            'category': [self.category.pk]
            }
        response = self.client.put(self.url, data=json.dumps(body), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = Post.objects.get(pk = self.post2.pk) 
        self.assertEqual(response.data['title'], expected_data.title)
    
    def test_put_admin(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
            'content_type': 'application/json',
        }
        body = {
            'title': 'Updated title from admin',
            'body': self.post2.body,
            'user_id': self.post2.user_id_id,
            'status': self.post2.status,
            'min_read': self.post2.min_read,
            'description': 'Test Description admin',
            'category': [self.category.pk]
            }
        response = self.client.put(self.url, data=json.dumps(body), **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_put_unregistered_user(self):

        body = {
            'title': 'Updated title from unregistered user',
            'body': self.post2.body,
            'user_id': self.post2.user_id_id,
            'status': self.post2.status,
            'min_read': self.post2.min_read,
            'description': 'Test Description unregistered',
            'category': [self.category.pk]
            }
        response = self.client.put(self.url, data=body)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_put_registered_not_owner(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token2.key}',
            'content_type': 'application/json',
        }
        body = {
            'title': 'Updated title from registered not owner user',
            'body': self.post2.body,
            'user_id': self.post2.user_id_id,
            'status': self.post2.status,
            'min_read': self.post2.min_read,
            'description': 'Test Description registered not owner user',
            'category': [self.category.pk]
            }
        response = self.client.put(self.url, data=body, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_unregistered_user(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_by_post_owner(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }

        response = self.client.delete(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_by_post_owner(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token2.key}',
            'content_type': 'application/json',
        }

        response = self.client.delete(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class PostCreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', password='testpassword')
        
        self.admin = User.objects.create(username='testuser2', password='testpassword2')
        self.admin_role = Role.objects.create(user=self.admin, is_admin=True)
        self.admin_token = Token.objects.create(user=self.admin)

        self.moderator = User.objects.create(username='moderator', password='testpassword3')
        self.moderator_role = Role.objects.create(user=self.moderator, is_moderator=True)
        self.moderator_token = Token.objects.create(user=self.moderator)
        
        self.blogger = User.objects.create(username='blogger', password='blogger')
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)
        
        self.role = Role.objects.create(user=self.user, is_admin=True, is_moderator=True, is_blogger=True)
        self.category = Category.objects.create(category_name='Test post Category')
        self.post = Post.objects.create(
            title='Test post Post',
            body='Test post Body',
            user_id=self.user,
            status='published',
            min_read='5 mins',
            description='Test post Description'
        )
        self.post.category.add(self.category)
        
        self.post2 = Post.objects.create(
            title='Test post Post2',
            body='Test post  Body2',
            status='published',
            min_read='5 mins',
            description='Test post Description2',
            user_id=self.blogger
        )
        self.post2.category.add(self.category)
        self.url = reverse('not_a_boring_blog:post-create') 
    
    def test_post_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        body = {
            'title': self.post2.title,
            'body': 'Some test body',
            'status': self.post2.status,
            'min_read': self.post2.min_read,
            'description': self.post2.description,
            'category': [self.category.pk]
            }

        response = self.client.post(self.url, data=json.dumps(body), **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_post_admin(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
            'content_type': 'application/json',
        }
        body = {
            'title': self.post2.title,
            'body': 'Some test body from admin',
            'status': self.post2.status,
            'min_read': self.post2.min_read,
            'description': self.post2.description,
            'category': [self.category.pk]
            }

        response = self.client.post(self.url, data=json.dumps(body), **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_post_moderator(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.moderator_token.key}',
            'content_type': 'application/json',
        }
        body = {
            'title': self.post2.title,
            'body': 'Some test body from moderator',
            'status': self.post2.status,
            'min_read': self.post2.min_read,
            'description': self.post2.description,
            'category': [self.category.pk]
            }

        response = self.client.post(self.url, data=json.dumps(body), **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_unregistered_user(self):
        body = {
            'title': self.post.title,
            'body': 'Some test body2',
            'status': self.post.status,
            'min_read': self.post.min_read,
            'description': self.post.description,
            'category': [self.category.pk]
            }

        response = self.client.post(self.url, data=body)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class GetPublicPostsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', password='testpassword')
        
        self.admin = User.objects.create(username='testname', password='testpassword!')
        self.admin_token = Token.objects.create(user=self.admin)
        self.role = Role.objects.create(user=self.admin, is_admin=True, is_moderator=True, is_blogger=True)
        
        self.moderator = User.objects.create(username='moderator', password='testpassword3')
        self.moderator_role = Role.objects.create(user=self.moderator, is_moderator=True)
        self.moderator_token = Token.objects.create(user=self.moderator)
        
        self.blogger = User.objects.create(username='blogger', password='blogger')
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)
        
        self.category = Category.objects.create(category_name='Test Category')
        self.post = Post.objects.create(
            title='Test get public Post by admin',
            body='Test get public Body by admin',
            user_id=self.admin,
            status='published',
            min_read='5 mins',
            description='Test get public Description',
        )
        self.post.category.add(self.category)
        self.url = reverse('not_a_boring_blog:get-public-posts')

    def test_list_admin(self):
        headers = {
                    'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
                    'content_type': 'application/json',
                }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_allow_all(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class GetUserPublicPostsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', password='testpassword')
        
        self.admin = User.objects.create(username='testadmin', password='testadminpassword!')
        self.admin_token = Token.objects.create(user=self.admin)
        self.admin_role = Role.objects.create(user=self.admin, is_admin=True)
        
        self.blogger = User.objects.create(username='blogger', password='blogger')
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)
        
        self.category = Category.objects.create(category_name='Test Category')
        self.post = Post.objects.create(
            title='Test get public only user Post by admin',
            body='Test get public only user Body by admin',
            user_id=self.admin,
            status='published',
            min_read='5 mins',
            description='Test get public only user Description',
        )
        self.post.category.add(self.category)
        
        self.post2 = Post.objects.create(
            title='Test get public only user Post by blogger',
            body='Test get public only user Body by blogger',
            user_id=self.blogger,
            status='published',
            min_read='5 mins',
            description='Test get public only user Description by blogger',
        )
        self.post2.category.add(self.category)
        self.url = reverse('not_a_boring_blog:only-user-posts', kwargs={'username': self.blogger.username})

    def test_get_user_public_admin(self):
        headers = {
                    'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
                    'content_type': 'application/json',
                }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_allow_all(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_user_public_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class GetUserPostsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', password='testpassword')
        
        self.admin = User.objects.create(username='testadmin', password='testadminpassword!')
        self.admin_token = Token.objects.create(user=self.admin)
        self.admin_role = Role.objects.create(user=self.admin, is_admin=True)
        
        self.blogger = User.objects.create(username='blogger', password='blogger')
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)
        
        self.category = Category.objects.create(category_name='Test Category')
        self.post = Post.objects.create(
            title='Test get all user Posts by admin',
            body='Test get all user Body by admin',
            user_id=self.admin,
            status='published',
            min_read='5 mins',
            description='Test get all user Description',
        )
        self.post.category.add(self.category)
        
        self.post2 = Post.objects.create(
            title='Test get all user Post by blogger',
            body='Test get all user Body by blogger',
            user_id=self.blogger,
            status='published',
            min_read='5 mins',
            description='Test get all user Description by blogger',
        )
        self.post2.category.add(self.category)
        self.url = reverse('not_a_boring_blog:my-posts')

    def test_get_all_user_posts_by_admin(self):
        headers = {
                    'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
                    'content_type': 'application/json',
                }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_user_posts_by_unregistered_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_all_user_posts_by_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

