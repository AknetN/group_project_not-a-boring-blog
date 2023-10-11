from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from ..models.post import Post
from ..models.repost_request import RepostRequest
from ..serializers.posts import (
    PostSerializer, 
    PostCreateSerializer, 
    PostUpdateSerializer,
    HidePostSerializer,
    )
from ..permissions import IsOwnerOrReadOnly, IsAdminRole, IsModeratorRole
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..models.user import Role, User
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Q

class PostList(APIView):
    """***This API lists all posts irrespective of their status***<p>
    <b>Requirements</b>:
    - The user must be authenticated and have a role of Admin or Moderator.
    - The user will need to use the token of Admin or Moderator<p>
     ***HOW TO USE:***<p>
    <b>1.1.</b>  Before making a request to this endpoint, ensure that you are authenticated. <p>
    ---> For this check <i><u>user/registration/</u></i> and <i><u>user/login/</u></i>.<p>    
    <b>1.2.</b> Apply the token, it should belong to <b>Admin</b> or <b>Moderator</b>. <p>
    !!! For this follow the steps:<p>
    ---> click on the image of a <b>lock</b> in the right corner of your highlighted box, <p> 
    ---> choose <b><i>tokenAuth</i></b>,<p> 
    ---> insert <b>Token</b> <b><i>MODERATOR_OR_ADMIN_TOKEN_KEY</i></b> and <b>Authorize</b>.<p>
    <b>1.3.</b> In order to get a list of all posts of all users <b>('published', 'editing', 'private')</b>, click on <b><i>Try it out</i></b> button.<p>
    <b>1.4.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>GET</b> request to the API endpoint.<p>
    ---> If successful, the API will return a json list of all existing posts. <p>
    ---> If there are any errors, appropriate error messages will be returned.<p>
    """
    permission_classes = [IsAuthenticated, IsAdminRole | IsModeratorRole]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=200) # or status=200


class PostCreate(APIView):
    '''***This API allows the creation of a new post***<p>
    <b>Requirements</b>:
    - The user must be authenticated.
    - The user will need to use their token.
    - The body text you provide should not yet exist in the database.<p>

    ***HOW TO USE:***<p>
    <ul><b>1. AUTHENTICATION</b><p>
    <ul><b>1.1.</b>  Before making a request to this endpoint, ensure that you are authenticated, using your token. <p>
    ---> For this check <i><u>user/registration/</u></i> and <i><u>user/login/</u></i>.<p>    
    <b>1.2.</b> Apply the token, it should belong to the authenticated user.<p>
    !!! For this follow the steps:<p>
    ---> click on the image of a <b>lock</b> in the right corner of your highlighted box, <p> 
    ---> choose <b><i>tokenAuth</i></b>,<p> 
    ---> insert <b>Token</b> <b><i>YOUR_TOKEN_KEY</i></b> and <b>Authorize</b>.<p>
    ------------------------------------------------------------<p>
    <b>2. BODY</b>:<p>
    <b>2.1.</b> In order to add <b>json</b> information to the <b>body</b>, click on <b><i>Try it out</i></b> button.<p>
    <b>2.2.</b> In the request body (application/json), provide information in such format:<p>
        <b><i>{
                "title": "string",
                "category": [1, 3],
                "status": "published",
                "min_read": "string",
                "description": "string",
                "body": "unique text"
                }</i></b><p>
    <b>2.3.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>POST</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 201 message along with the code itself. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
    '''
    
    serializer_class = PostCreateSerializer

    def post(self, request):
        user_id = request.user.id  # Get the user_id from the request
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id_id=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class PostDetail(APIView):
    '''***Provides detailed view of a separate post. <p>
    Also allows updating and deleting a post.*** <p>  
    
    ***HOW TO USE:***<p>
    <ul><b>1. AUTHENTICATION</b><p>
    <ul><b>1.1.</b>  Before making a request to this endpoint, ensure that you are authenticated, using your token. <p>
    ---> For this check <i><u>user/registration/</u></i> and <i><u>user/login/</u></i>.<p>    
    <b>1.2.</b> Apply the token, it should belong to the authenticated user.<p>
    !!! For this follow the steps:<p>
    ---> click on the image of a <b>lock</b> in the right corner of your highlighted box, <p> 
    ---> choose <b><i>tokenAuth</i></b>,<p> 
    ---> insert <b>Token</b> <b><i>YOUR_TOKEN_KEY</i></b> and <b>Authorize</b>.<p>
    ------------------------------------------------------------<p>
    '''
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = PostUpdateSerializer

    def get_post(self, pk):        
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None

    def get(self, request, pk):
        '''***Here the authenticated user can only see a separate post***<p>
        <b>Requirements</b>:<p>
        - The user must be authenticated.<p>
        - The user will need to use their token.<p>
    
    <ul><b>1. RETRIEVING</b>:<p>
    <ul><b>1.1.</b> In order to get <b>json</b> information of a separate post, click on <b><i>Try it out</i></b> button.<p>
    <b>1.2.</b> In the <b><i>id integer path</i></b> provide an <b>id number</b> of the existing post. <p>
    <b>1.3.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>GET</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with the code itself. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
        '''      
        post = self.get_post(pk)
        if post:
            if not IsOwnerOrReadOnly().has_object_permission(request, self, post):
                return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            serializer = PostSerializer(post)            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        '''***This API allows the authenticated user update their own Post***<p>

    <ul><b>1. UPDATING</b>:<p>
    <ul><b>1.1.</b> In order to put <b>json</b> information, click on <b><i>Try it out</i></b> button.<p>
    <b>1.2.</b> In the <b><i>id integer path</i></b> provide an <b>id number</b> of the existing post, 
    then in <b><i>Request body</i></b> update your information.<p>
    <b>1.3.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>PUT</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with <b><i>created_at</i></b> and <b><i>last_updated</i></b> information as well. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>'''
    
        post = self.get_post(pk)
        if post:
            if str(request.user) != str(post.user_id):
                return Response({"detail": "Permission denied"}, status=403)
            serializer = PostUpdateSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                categories = request.data['category']
                post.update_categories(categories)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        '''***This API allows the authenticated user delete their own Post***<p>
    <ul><b>1. DELETING</b>:<p>
    <ul><b>1.1.</b> In order to delete a post, click on <b><i>Try it out</i></b> button.<p>
    <b>1.2.</b> In the <b><i>id integer path</i></b> provide an <b>id number</b> of the post you want to delete.<p>
    <b>1.3.</b> Press the <b><i>Execute</i></b> button in order to send a <b>DELETE</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 204 message.<p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>'''
    
        post = self.get_post(pk)
        if post and post.user_id == request.user:
            post.delete()
            return Response({"detail": "Deletion is done"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)


class GetPublicPosts(APIView):
    '''***This API fetches all posts that have status "published"***<p>
    <b>Requirements</b>:<p>
    - All users, including unauthenticated, can see all posts in 'published' status.

    ***HOW TO USE:***<p>
    <ul><b>1.1.</b> In order to get a <b>json</b> list of all public posts, click on <b><i>Try it out</i></b> button.<p>
    <b>1.2.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>GET</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with the json list of posts.<p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>'''
    
    permission_classes = [AllowAny]

    def get(self, request):
        public_posts = Post.objects.filter(status='published')
        serializer = PostSerializer(public_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetUserPublicPosts(APIView):
    '''***This API allows to fetch all 'published' posts of a specified user***<p>
    <b>Requirements</b>:<p>
    - All users, including unauthenticated, can see all posts in 'published' status of a separate user.
    
   ***HOW TO USE:***<p>
    <ul><b>1.1.</b> In order to get a <b>json</b> list of all posts of a separate user, click on <b><i>Try it out</i></b> button.<p>
    <b>1.2.</b> In the <b><i>username string path</i></b> provide a <b>username</b> of the post author.<p>
    <b>1.3.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>GET</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with the json list of this user posts.<p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>'''
    serializer_class = PostSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        username = self.kwargs['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": f"{username} not found"}, status.HTTP_404_NOT_FOUND)
        user_posts = Post.objects.filter(user_id=user, status='published')
        approved_repost_requests = RepostRequest.objects.filter(requester_id=user, status='approved')
        reposted_posts = [repost_request.post_id for repost_request in approved_repost_requests]
        reposted_post_ids = [post.id for post in reposted_posts]
        reposted_posts_query = Q(id__in=reposted_post_ids)
        queryset = user_posts | Post.objects.filter(reposted_posts_query)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({"detail": f"{self.kwargs['username']} has no posts"}, status=status.HTTP_200_OK)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetUserPosts(ListAPIView):
    """***This API lists all your own posts irrespective of their status***<p>
    <b>Requirements</b>:
    - The user must be authenticated with their own token.<p>
     ***HOW TO USE:***<p>
    <b>1.1.</b>  Before making a request to this endpoint, ensure that you are authenticated. <p>
    ---> For this check <i><u>user/registration/</u></i> and <i><u>user/login/</u></i>.<p>    
    <b>1.2.</b> Apply the token, it should belong to the authenticated user (you).<p>
    !!! For this follow the steps:<p>
    ---> click on the image of a <b>lock</b> in the right corner of your highlighted box, <p> 
    ---> choose <b><i>tokenAuth</i></b>,<p> 
    ---> insert <b>Token</b> <b><i>YOUR_TOKEN_KEY</i></b> and <b>Authorize</b>.<p>
    <b>1.3.</b> In order to get a list of all your posts <b>('published', 'editing', 'private')</b>, click on <b><i>Try it out</i></b> button.<p>
    <b>1.4.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>GET</b> request to the API endpoint.<p>
    ---> If successful, the API will return a json list of all existing posts. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul><p>
    """
    serializer_class = PostSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.filter(user_id=user)
        get_list_or_404(queryset)
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HidePost(generics.UpdateAPIView):
    """Only accessible to moderators:

    - Need to use a moderator token for authentication;

    If the post is not written according to the general guidelines, the moderator can hide the post,
    post will be set to editing.

    Simply insert the post id and execute, when you try to visualize the user public post, the just
    hidden post shouldn't be visible anymore;
    """
    permission_classes = [IsModeratorRole]
    serializer_class = HidePostSerializer

    def put(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = HidePostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)