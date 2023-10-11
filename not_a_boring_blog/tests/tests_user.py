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
from django.contrib.auth.hashers import make_password


class ChangeUserPasswordTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.url = reverse('not_a_boring_blog:change_password')


    def test_change_password_by_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        data = {
            'current_password': 'bloggerpass',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123',
        }
        response = self.client.put(self.url, data=json.dumps(data), **headers)
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_change_password_by_unregistered_user(self):
        data = {
            'current_password': 'passworduser',
            'new_password': 'newpassword1234',
            'confirm_password': 'newpassword1234',
        }
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_change_password_incorrect_current_password(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        data = {
            'current_password': 'incorrectpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123',
        }
        response = self.client.put(self.url, data=data, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_change_password_with_mismatched_new_passwords(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        data = {
            'current_password': 'bloggerpass',
            'new_password': 'newpassword123',
            'confirm_password': 'mismatchedpassword',
        }
        response = self.client.put(self.url, data=json.dumps(data), **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class UpdateUserRoleTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.admin = User.objects.create(username='admin', password=make_password('adminpass'))
        self.admin_role = Role.objects.create(user=self.admin, is_admin=True)
        self.admin_token = Token.objects.create(user=self.admin)

        self.moderator = User.objects.create(username='moderator', password=make_password('moderatorpass'))
        self.moderator_role = Role.objects.create(user=self.moderator, is_moderator=True)
        self.moderator_token = Token.objects.create(user=self.moderator)

        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  


        self.url = reverse('not_a_boring_blog:update_role', kwargs={'username': self.blogger.username})
        
        
    def test_update_user_role_by_admin(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
            'content_type': 'application/json',
        }
        data = {
            'role': {
                'is_blogger': False, 
                'is_moderator': False,
                'is_admin': True,
            }
        }
        response = self.client.put(self.url, data=json.dumps(data), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    
    def test_update_user_role_by_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        data = {
            'role': {
                'is_blogger': False, 
                'is_moderator': True,
                'is_admin': False,
            }
        }
        response = self.client.put(self.url, data=json.dumps(data), **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_update_user_role_for_nonexistent_user(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
            'content_type': 'application/json',
        }
        data = {
            'role': {
                'is_blogger': False,
                'is_moderator': False,
                'is_admin': False,
            }
        }
        url = reverse('not_a_boring_blog:update_role', kwargs={'username': 'nonexistentuser'})
        response = self.client.put(url, data=data, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_user_role_with_invalid_data(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
            'content_type': 'application/json',
        }
        # Missing 'role' key in data
        data = {
            'is_someone': False,
            'is_noone': True,
            'is_admin': True,
        }
        response = self.client.put(self.url, data=data, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class UserListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.admin = User.objects.create(username='admin', is_staff=True, password=make_password('adminpass'))
        # IsAdminUser doesn't understand is_admin Role, that's why we add it here
        self.admin_role = Role.objects.create(user=self.admin, is_admin=True)
        self.admin_token = Token.objects.create(user=self.admin)

        self.moderator = User.objects.create(username='moderator', password=make_password('moderatorpass'))
        self.moderator_role = Role.objects.create(user=self.moderator, is_moderator=True)
        self.moderator_token = Token.objects.create(user=self.moderator)

        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  


        self.url = reverse('not_a_boring_blog:users_list')
    
    
    def test_get_user_list_by_admin(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}',
            'content_type': 'application/json',
        }
        # data in GET is not applied
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_user_list_by_moderator(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.moderator_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    
    def test_get_user_list_by_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_user_list_by_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class RegisterUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('not_a_boring_blog:register')
    
    def test_successful_registration_role_blogger(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    

    def test_duplicate_username_registration(self):
        User.objects.create(username='existinguser', password='passworduser')
        data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_duplicate_email_registration(self):
        User.objects.create(username='newuser', email='existinguser@example.com', password='passworduser')
        data = {
            'username': 'newuser',
            'email': 'existinguser@example.com',
            'password': 'newpassword123',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class UpdateUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.url = reverse('not_a_boring_blog:update_user')
    
    
    def test_partial_update_blogger_info(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        data = {
            'username': 'new_blogger_name1',
        }
        response = self.client.put(self.url, data=json.dumps(data), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        '''Verify that only the 'username' field has been updated'''
        updated_user = User.objects.get(id=self.blogger.id)
        self.assertEqual(updated_user.username, 'new_blogger_name1')
        self.assertEqual(updated_user.email, self.blogger.email)  # Email remains the same
    
    
    def test_update_blogger_info(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        data = {
            'username': 'new_blogger_name',
            'email': 'bloggeremail@example.com',
            'bio': 'New blogger bio information.',
        }
        response = self.client.put(self.url, data=json.dumps(data), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        '''Verify that the user's information has been updated'''
        updated_blogger = User.objects.get(id=self.blogger.id)
        self.assertEqual(updated_blogger.username, 'new_blogger_name')
        self.assertEqual(updated_blogger.email, 'bloggeremail@example.com')

        '''Verify that the associated Role's 'bio' field has been updated'''
        role = Role.objects.get(user=updated_blogger)
        # self.assertEqual(role.bio, 'New blogger bio information.')


    def test_partial_update_unauthorized_user(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class LoginUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.blogger = User.objects.create(username='blogger', email='test_blogger@example.com', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  

        self.url = reverse('not_a_boring_blog:login')
    
    
    def test_login_with_username(self):
        data = {
            'username': 'blogger',
            'password': 'bloggerpass',
        }
        response = self.client.post(self.url, data=data, format='json') 
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_login_with_email(self):
        data = {
            'email': 'test_blogger@example.com',
            'password': 'bloggerpass',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_login_with_invalid_credentials(self):
        data = {
            'username': 'blogger',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_login_with_missing_credentials(self):
        data = {
            'password': 'bloggerpass',
        }
        response = self.client.post(self.url, data=data, format='json')
        #print(response.content)  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_login_with_nonexistent_user(self):
        data = {
            'username': 'nonexistentuser',
            'password': 'bloggerpass',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LogoutUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='passworduser')
        
        self.admin = User.objects.create(username='admin', password=make_password('adminpass'))
        self.admin_role = Role.objects.create(user=self.admin, is_admin=True)
        self.admin_token = Token.objects.create(user=self.admin)

        self.moderator = User.objects.create(username='moderator', password=make_password('moderatorpass'))
        self.moderator_role = Role.objects.create(user=self.moderator, is_moderator=True)
        self.moderator_token = Token.objects.create(user=self.moderator)

        self.blogger = User.objects.create(username='blogger', password=make_password('bloggerpass'))
        self.blogger_role = Role.objects.create(user=self.blogger, is_blogger=True)
        self.blogger_token = Token.objects.create(user=self.blogger)  


        self.url = reverse('not_a_boring_blog:logout')
    
    
    def test_logout_by_blogger(self):
        headers = {
            'HTTP_AUTHORIZATION': f'Token {self.blogger_token.key}',
            'content_type': 'application/json',
        }
        response = self.client.get(self.url, **headers)
        #print(response.content)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated_user(self):
        response = self.client.get(self.url)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        