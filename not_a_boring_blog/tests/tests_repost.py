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
from ..models.repost_request import RepostRequest, STATUS



class CreateRepostRequestTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.post = Post.objects.create(
            title='Test post Post',
            body='Test post Body',
            user_id=self.blogger,
            status='published',
            min_read='5',
            description='Test post Description'
        )
        self.url = reverse('not_a_boring_blog:request_repost', kwargs={'post_id': self.post.id})


    def test_create_repost_request(self):
        """Test creating a repost request"""
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.post(self.url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_duplicate_repost_request(self):
        """Test creating a duplicate repost request"""
        # Create a repost request for the same post
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        RepostRequest.objects.create(requester_id=self.blogger, post_id=self.post, status='requested')
        response = self.client.post(self.url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_repost_request_unauthenticated(self):
        """Test creating a repost request without authentication"""
        response = self.client.post(self.url)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# there is no reason to check 404 error, while according to serializer default, there always be requested (201)


class RepostRequestedReceivedListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.post = Post.objects.create(
            title='Test post Post',
            body='Test post Body',
            user_id=self.blogger,
            status='published',
            min_read='5',
            description='Test post Description'
        )
        self.url = reverse('not_a_boring_blog:requests_received')


    def test_repost_requests_received_list(self):
        """Test retrieving a list of repost requests received by the post owner"""
        repost_request = RepostRequest.objects.create(
            requester_id=self.user,
            post_id=self.post,
            status='requested'
        )
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.get(self.url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #print(len(response.data)) # Assert that the serialized repost request is present in the response data


    def test_repost_requests_received_list_unauthenticated(self):
        """Test retrieving a list of repost requests received when unauthenticated"""
        response = self.client.get(self.url)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RepostRequestsSentListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.post = Post.objects.create(
            title='Test post Post',
            body='Test post Body',
            user_id=self.blogger,
            status='published',
            min_read='5',
            description='Test post Description'
        )
        self.url = reverse('not_a_boring_blog:requests_sent')
    
    
    def test_repost_requests_sent_list(self):
        """Test retrieving a list of repost requests sent by the user"""
        repost_request = RepostRequest.objects.create(
            requester_id=self.blogger,
            post_id=self.post,
            status='requested'
        )
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.get(self.url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #print(len(response.data))
        self.assertEqual(len(response.data), 1) # Assert that the serialized repost request is present in the response data


    def test_repost_requests_sent_list_unauthenticated(self):
        """Test retrieving a list of repost requests sent when unauthenticated"""
        response = self.client.get(self.url)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class UpdateRepostRequestStatusTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.post = Post.objects.create(
            title='Test post Post',
            body='Test post Body',
            user_id=self.blogger,
            status='published',
            min_read='5',
            description='Test post Description'
        )
        
        self.repost_request = RepostRequest.objects.create(
            requester_id=self.blogger,
            post_id=self.post,
            status='requested'
        )
        self.url = reverse('not_a_boring_blog:request_update', kwargs={'request_id': self.repost_request.id})
    
    
    def test_update_repost_request_status(self):
        """Test updating the status of a repost request"""
        new_status = "approved"  # Update the status to 'approved'
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.put(self.url, data=f'{{"status": "{new_status}"}}', **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #print(self.repost_request.refresh_from_db()) # as a result it gets None because it doesn't return anything
        self.repost_request.refresh_from_db()  #we should necessarily refresh the repost request from the database, otherwise we'll have 'AssertionError: 'requested' != 'approved''
        #print(self.repost_request.status, new_status)
        self.assertEqual(self.repost_request.status, new_status)


    def test_update_repost_request_invalid_status(self):
        """Test updating the status of a repost request with an invalid status"""
        invalid_status = 'invalid_status'
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.put(self.url, data=f'{{"status": "{invalid_status}"}}', **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #print(self.repost_request.refresh_from_db()) 
        self.repost_request.refresh_from_db()
        #print(self.repost_request.status, invalid_status)        
        self.assertNotEqual(self.repost_request.status, invalid_status) # Check if the status has not been updated


    def test_update_repost_request_not_found(self):
        """Test updating the status of a non-existent repost request"""
        non_existent_request_id = self.repost_request.id + 100  # A non-existent request ID
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        url = reverse('not_a_boring_blog:request_update', kwargs={'request_id': non_existent_request_id})
        response = self.client.put(url, data={'status': 'approved'}, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class DeleteRepostRequestViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.post = Post.objects.create(
            title='Test post Post',
            body='Test post Body',
            user_id=self.blogger,
            status='published',
            min_read='5',
            description='Test post Description'
        )
        
        self.repost_request = RepostRequest.objects.create(
            requester_id=self.blogger,
            post_id=self.post,
            status='requested'
        )
        self.url = reverse('not_a_boring_blog:delete_repost_request', kwargs={'request_id': self.repost_request.id})
    
    def test_delete_repost_request(self):
        """Test deleting a repost request by ID"""
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.delete(self.url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_delete_nonexistent_repost_request(self):
        """Test deleting a nonexistent repost request"""
        nonexistent_id = self.repost_request.id + 100  # ID that doesn't exist
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        url = reverse('not_a_boring_blog:delete_repost_request', kwargs={'request_id': nonexistent_id})
        response = self.client.delete(url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        

    def test_delete_repost_request_unauthorized(self):
        """Test deleting a repost request without authorization"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_delete_repost_request_forbidden(self):
        """Test deleting a repost request for a different user"""
        another_user = User.objects.create(username='another_user', password='anotherpassword')
        another_user_token = Token.objects.create(user=another_user)
        headers = {
            'HTTP_AUTHORIZATION': f'Token {another_user_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.delete(self.url, **headers)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)