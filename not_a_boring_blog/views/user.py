from rest_framework.views import APIView
from not_a_boring_blog.models.user import Role
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from not_a_boring_blog.serializers.user import (
    RoleSerializer,
    CustomUserSerializer,
    LoginUserSerializer,
    UpdateRoleSerializer,
    ChangePasswordSerializer,
    UpdateUserSerializer,
    UpdateUserBioSerializer,
    UserListSerializer,
)
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from not_a_boring_blog.permissions import IsAdminRole


class UserList(APIView):
    """
    Returns the entire list of users on the platform.

    - All users should be able to see this list;

    To test you will need a Token:

    - You can get one by using the user/login/ APIView if you have an account or user/register/ APIView and after, log in with the credentials
    Token will be returned in response after a successful login, copy this <u>TokenAuthKey</u>
    (name may differ, look for a key that contains token in its name);
    - Press on the little lock for users_list view call (you should see it on the right);
    - Scroll down and go to TokenAuth;
    - In this field you'll need to have something similar to: Token <u>TokenAuthKey</u>
    <- this should be in you clipboard from the previous steps;
    - Press <b>Try it out</b> button then <b>Execute</b>;

    You should now see a Curl request, URL request and the Response with all users or an error message,
    if not scroll a little bit down.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateUserRole(APIView):
    """
    Used to update user role.

    - Only users with Admin role can use this view;

    To test you will need a Token from Admin role user:

    - You can get one by using the user/login/ APIView with username:"admin" and pass:"admin1234".
    Token will be returned in response after a successful login, copy this <u>TokenAuthKey</u>
    (name may differ, look for a key that contains token in its name);
    - Press on the little lock for users_list view call (you should see it on the right);
    - Scroll down and go to TokenAuth;
    - In this field you'll need to have something similar to: Token <u>TokenAuthKey</u>
    <- this should be in you clipboard from the previous steps;
    - Press <b>Try it out</b>;
    - You'll need to put in the username of the user of whose role will be updated;
    - Go in the Request Body section and set role to true; (Only one role can be set to true at a time)
    - Press <b>Execute</b> and check Response Body for result;
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = UpdateRoleSerializer

    def put(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role.is_admin:
            serializer = UpdateRoleSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"details":"You do not have permission for this operation"}, status=status.HTTP_403_FORBIDDEN)


class RegisterUser(APIView):
    """
    Used to register user.

    - This action is allowed to all users;

    To test this APIView:

    - Press <b>Try it out</b>;
    - Scroll down to request body and insert values for username, email and password;
    - Press <b>Execute</b> and check Response Body for result;
    """
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')
            # Check if a user with the same email or username already exists
            if User.objects.filter(Q(username=username)).exists():
                return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(Q(email=email)).exists():
                return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUser(APIView):
    """
    Used to update user information - username, email.

    - User needs to be authorized;

    To test you will need the user token, token is generated when user logs in:

    - You can get one by using the user/login/ APIView ->
    for this you need an already registered user with user/register APIView.
    - Token will be returned in response after a successful login, copy this <u>TokenAuthKey</u>
    (name may differ, look for a key that contains token in its name);
    - Press on the little lock for users_list view call (you should see it on the right);
    - Scroll down and go to TokenAuth;
    - In this field you'll need to have something similar to: Token <u>TokenAuthKey</u>
    <- this should be in you clipboard from the previous steps;
    - Press <b>Try it out</b>;
    - Go to Request Body, update the values (<b>Important to know!</b> Because it would take 2 requests, the Request body
    displayed by swagger is filled with dummy data, but it will be updated to the user if executed. On frontend the
    information of the user is first retrieved, and then it updated accordingly)
    - Press <b>Execute</b> and check Response Body for result;
    """
    serializer_class = UpdateUserSerializer

    def put(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            new_email = serializer.validated_data.get('email')
            if new_email and User.objects.filter(email=new_email).exclude(id=user.id).exists():
                return Response({"details": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserBio(APIView):
    """
        Used to update user bio.

        - User needs to be authorized;

        To test you will need the user token, token is generated when user logs in:

        - You can get one by using the user/login/ APIView ->
        for this you need an already registered user with user/register APIView.
        - Token will be returned in response after a successful login, copy this <u>TokenAuthKey</u>
        (name may differ, look for a key that contains token in its name);
        - Press on the little lock for users_list view call (you should see it on the right);
        - Scroll down and go to TokenAuth;
        - In this field you'll need to have something similar to: Token <u>TokenAuthKey</u>
        <- this should be in you clipboard from the previous steps;
        - Press <b>Try it out</b>;
        - Go to Request Body, update the values (<b>Important to know!</b> Because it would take 2 requests, the Request body
        displayed by swagger is filled with dummy data, but it will be updated to the user if executed. On frontend the
        information of the user is first retrieved, and then it updated accordingly)
        - Press <b>Execute</b> and check Response Body for result;
        """
    serializer_class = UpdateUserBioSerializer

    def get(self, request):
        self.permission_classes = [AllowAny]
        try:
            role = Role.objects.get(user=request.user)
        except Role.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"bio": role.bio}, status.HTTP_200_OK)
    def put(self, request):
        try:
            role = Role.objects.get(user=request.user)
        except Role.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateUserBioSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            role.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserPassword(APIView):
    """
    Used to change user password.

    - User needs to be authorized;

    To test you will need the user token, token is generated when user logs in:

    - You can get one by using the user/login/ APIView ->
    for this you need an already registered user with user/register APIView.
    - Token will be returned in response after a successful login, copy this <u>TokenAuthKey</u>
    (name may differ, look for a key that contains token in its name);
    - Press on the little lock for users_list view call (you should see it on the right);
    - Scroll down and go to TokenAuth;
    - In this field you'll need to have something similar to: Token <u>TokenAuthKey</u>
    <- this should be in you clipboard from the previous steps;
    - Press <b>Try it out</b>;
    - Go to Request Body and change the values of the attributes;
    - Press <b>Execute</b> and check Response Body for result;
    """
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('current_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)  # To update session after password change
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUser(APIView):
    """
    Used to log in user.

    - This action can be performed by all users;
    - <u>At log in a token is being created, all authorized actions can only be performed with this Token;</u>

    To test you will need to have a registered user:

    - Go to user/register_user/ to register a user if you don't have one already;
    - Press <b>Try it out</b>;
    - In Request Body insert username or email and password (leave an empty string for the value you don't fill*);
    - Press <b>Execute</b> and check Response Body for result;
    """
    permission_classes = [AllowAny]
    serializer_class = LoginUserSerializer

    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data.get("username") or serializer.data.get("email"):
                username = ''
                email = ''
                if serializer.data.get("username"):
                    username = serializer.data.get("username").lower()
                    try:
                        user_exists = User.objects.filter(username=username).first()                        
                    except User.DoesNotExist:
                        return Response({"detail": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
                if serializer.data.get("email"):
                    email = serializer.data.get("email").lower()
                    try:
                        user_exists = User.objects.filter(email=email).first()                        
                    except User.DoesNotExist:
                        return Response({"detail": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)                       
            else:
                return Response({"detail": "You need to provide username or email in order to log in!"}, status=status.HTTP_400_BAD_REQUEST)
            password = serializer.data.get("password")
            user = authenticate(username=user_exists, password=password)
            if user is not None:                
                token, created = Token.objects.get_or_create(user=user)
                try:
                    role = Role.objects.get(user=user)
                    role_serializer = RoleSerializer(role)
                    true_roles = {}  # Dictionary key-value pairs of true roles
                    for key, value in role_serializer.data.items():
                        if value:
                            true_roles[key] = value
                except Role.DoesNotExist:
                    true_roles = None
                data = {
                    "token": str(token),
                    "username": str(user_exists),
                    "role": true_roles
                }
                return Response(data, status=200)
            else:
                return Response({"detail": "Wrong credentials."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutUser(APIView):
    """
    Used to log out user.

    - Deletes user Authentication token;
    - User needs to be logged in;

    To test you will need the user token, token is generated when user logs in:
    - You can get one by using the user/login/ APIView ->
    for this you need an already registered user with user/register APIView.
    - Token will be returned in response after a successful login, copy this <u>TokenAuthKey</u>
    (name may differ, look for a key that contains token in its name);
    - Press on the little lock for users_list view call (you should see it on the right);
    - Scroll down and go to TokenAuth;
    - In this field you'll need to have something similar to: Token <u>TokenAuthKey</u>
    <- this should be in you clipboard from the previous steps;
    - Press <b>Try it out</b>;
    - Press <b>Execute</b> and check Response Body for result;
    """
    def get(self, request, format=None):
        # simply delete the token to force a logout
        try:
            request.user.auth_token.delete()
            return Response({"detail": f"Goodbye, {request.user}!"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "You are not logged in!"}, status=status.HTTP_404_NOT_FOUND)