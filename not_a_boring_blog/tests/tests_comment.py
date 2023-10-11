from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from ..models.comment import Comment
from ..models.post import Post
from ..models.user import Role
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json



class PostCommentListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password='blogger')
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)
                
        self.post = Post.objects.create(
            title='Sample Post',
            body='Sample Body',
            user_id=self.blogger,
            status='published',
            min_read='5 mins',
            description='Sample Description'
        )     

        self.url = reverse('not_a_boring_blog:comments', kwargs={'post_id': self.post.id})


    def test_list_comments_unauthorized(self):
        self.comment1 = Comment.objects.create(post_id=self.post, author=self.blogger, body='Comment 1')
        self.comment2 = Comment.objects.create(post_id=self.post, author=self.blogger, body='Comment 2')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_list_comments_authorized(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        self.comment1 = Comment.objects.create(post_id=self.post, author=self.blogger, body='Comment 3')
        self.comment2 = Comment.objects.create(post_id=self.post, author=self.blogger, body='Comment 4')
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_list_comments_no_comments(self):
        Comment.objects.filter(post_id_id=self.post.id).delete()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class CreateCommentTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password='blogger')
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)
                
        self.post = Post.objects.create(
            title='Sample Post',
            body='Sample Body',
            user_id=self.blogger,
            status='published',
            min_read='5 mins',
            description='Sample Description'
        )     
        self.url = reverse('not_a_boring_blog:create_comment', kwargs={'post_id': self.post.id})

    def test_if_post_does_not_exist(self):
        non_existent_post_id = 11111
        url = reverse('not_a_boring_blog:create_comment', kwargs={'post_id': non_existent_post_id})

        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        
        response = self.client.post(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 


    def test_create_comment_by_unregistered_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    
    def test_create_comment_by_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        body = {
            "body": "A sample comment"
        }        
        response = self.client.post(self.url, data=json.dumps(body), **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



class CreateReplyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password='blogger')
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)
                
        self.post = Post.objects.create(
            title='Sample Post',
            body='Sample Body',
            user_id=self.blogger,
            status='published',
            min_read='5 mins',
            description='Sample Description'
        )     
        
        self.comment = Comment.objects.create(
        post_id=self.post,
        author=self.blogger,
        body='Comment 1'
        )
        self.url = reverse('not_a_boring_blog:create_reply', kwargs={'comment_id': self.comment.id})
    
    
    def test_create_reply_by_authenticated_user(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        valid_data = {"body": "A sample reply"}
        response = self.client.post(self.url, data=json.dumps(valid_data), **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_reply_by_unauthenticated_user(self):
        valid_data = {"body": "A sample reply"}
        response = self.client.post(self.url, data=valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_reply_with_missing_body(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        invalid_data = {}  # Missing 'body' field
        response = self.client.post(self.url, data=invalid_data, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_reply_with_invalid_data(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        invalid_data = {'body': 'A' * 1000}  # max_length = 500
        response = self.client.post(self.url, data=json.dumps(invalid_data), **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_reply_to_nonexistent_comment(self):
        nonexistent_comment_id = self.comment.id + 1  # this comment does not exist
        url = reverse('not_a_boring_blog:create_reply', kwargs={'comment_id': nonexistent_comment_id})
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        valid_data = {'body': 'A sample reply'}
        response = self.client.post(url, data=valid_data, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class UpdateCommentTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password='blogger')
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)
                
        self.post = Post.objects.create(
            title='Sample Post',
            body='Sample Body',
            user_id=self.blogger,
            status='published',
            min_read='5 mins',
            description='Sample Description'
        )    
        self.comment = Comment.objects.create(
            post_id=self.post,
            author=self.blogger,
            body='Sample Comment'
        )
        self.url = reverse('not_a_boring_blog:update_comment', kwargs={'comment_id': self.comment.id})

    def test_get_comment_from_unauthorized_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_comment_from_authorized_user(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }        
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_nonexistent_comment(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }   
        url = reverse('not_a_boring_blog:update_comment', kwargs={'comment_id': 999})
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_comment_by_unauthorized_user(self):
        updated_data = {'body': 'Updated Comment'}
        response = self.client.put(self.url, data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        updated_data = {'body': 'Updated Comment'}
        response = self.client.put(self.url, data=json.dumps(updated_data), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment_by_other_user(self):
        another_user = User.objects.create(username='another_user', password='password')
        another_user_token = Token.objects.create(user=another_user)

        headers = {
            'HTTP_AUTHORIZATION': f'Token {another_user_token.key}',
            'content_type': 'application/json',
        }
        updated_data = {'body': 'Updated Comment'}
        response = self.client.put(self.url, data=updated_data, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_delete_comment(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }   
        response = self.client.delete(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_comment_by_other_user(self):
        another_user = User.objects.create(username='another_user', password='password')
        another_user_token = Token.objects.create(user=another_user)

        headers = {
            'HTTP_AUTHORIZATION': f'Token {another_user_token.key}',
        }
        response = self.client.delete(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)