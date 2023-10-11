from rest_framework import status, viewsets
from rest_framework.response import Response
from ..models.comment import Comment
from ..serializers.comment import (
    CommentSerializer,
    ReplyCommentSerializer,
)
from rest_framework.permissions import AllowAny
from ..permissions import IsModeratorRole
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from ..models.post import Post
from ..models.user import User
from django.http import Http404


class PostCommentList(APIView):
    """***This API gets all comments for a given post***<p>
    <b>Requirements</b>:<p>
    - No authentication is required to retrieve the comments.<p>
    
   ***HOW TO USE:***<p>    
    <ul><b>1.1.</b> In order to get a <b>json</b> list of comments for a separate post, click on <b><i>Try it out</i></b> button.<p>
    <b>1.2.</b> In the <b><i>post_id integer path</i></b> provide a <b>post_id</b> of the post you are interested in.<p>
    <b>1.3.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>GET</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with the json list of comments.<p>
    ---> If there are no comments, a 404 error with the message will be returned.<p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
    """
    permission_classes = [AllowAny]

    def get(self, request, post_id):

        comments = Comment.objects.filter(post_id=post_id, parent_id=None)  # Retrieve top-level comments (not replies)
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateComment(APIView):
    '''***This API allows the creation of a new comment for a public post***<p>
    <b>Requirements</b>:
    - The user must be authenticated.
    - The user will need to use the token.<p>

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
    <b>2.1.</b> In order to add <b>json</b> information to the <b>comment body</b>, click on <b><i>Try it out</i></b> button.<p>
    <b>2.2.</b> In the <b><i>post_id integer path</i></b> provide a <b>post_id</b> of the post you want to comment on.</p>
    <b>2.3.</b> In the request body (application/json), provide information for <b><i>{"body": "add your comment here"}</i></b><p>
    <b>2.4.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>POST</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 201 message along with the code itself. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
    '''
    serializer_class = ReplyCommentSerializer

    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id, status='published')  # Retrieve the associated post
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReplyCommentSerializer(data=request.data)
        if serializer.is_valid():
            # Set the comment's author to the authenticated user
            serializer.save(author=request.user, post_id=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateComment(APIView):
    '''***Provides detailed view of a separate comment*** <p>  
    
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
    serializer_class = ReplyCommentSerializer

    def get_comment(self, comment_id):
        try:
            return Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return None

    def get(self, request, comment_id):
        '''***Here the authenticated user can only get a separate comment***<p>
        <b>Requirements</b>:<p>
        - The user must be authenticated.<p>
        - The user will need to use their token.<p>
    
    <ul><b>1. RETRIEVING</b>:<p>
    <ul><b>1.1.</b> In order to get <b>json</b> information of a separate comment, click on <b><i>Try it out</i></b> button.<p>
    <b>1.2.</b> In the <b><i>post_id integer path</i></b> provide a <b>post_id</b> of the existing post. <p>
    <b>1.3.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>GET</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with the code itself. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
        '''      
        comment = self.get_comment(comment_id)
        if comment is None:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReplyCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, comment_id):
        '''***This API allows the authenticated user update their own comment***<p>
    <b>Before making a request to this endpoint, ensure that you are authenticated, using your token.</b> <p>
    <ul><b>1. UPDATING</b>:<p>
    <ul><b>1.1.</b> In order to update your own comment, click on <b><i>Try it out</i></b> button.<p>
    <b>1.2.</b> In the <b><i>comment_id integer path</i></b> provide a <b>comment_id</b> of your existing comment, 
    then in <b><i>Request body</i></b> update your information.<p>
    <b>1.3.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>PUT</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with <b><i>created_at</i></b> and <b><i>last_updated</i></b> information as well. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>'''

        comment = Comment.objects.get(pk=comment_id)
        if comment is None:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReplyCommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            # Check if the user making the request is the author of the comment.
            if comment.author != request.user:
                return Response({"detail": "You do not have permission to update this comment"}, status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        '''***This API allows the authenticated user delete their own comment***<p>
        <b>Before making a request to this endpoint, ensure that you are authenticated, using your token.</b> <p>

    <ul><b>1. DELETING</b>:<p>
    <ul><b>1.1.</b> In order to delete a post, click on <b><i>Try it out</i></b> button.<p>
    <b>1.2.</b> In the <b><i>id integer path</i></b> provide a <b>comment_id</b> of the comment you want to delete.<p>
    <b>1.3.</b> Press the <b><i>Execute</i></b> button in order to send a <b>DELETE</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message.<p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>'''
    
        '''Make a DELETE request with the comment_id. 
        Ensure you are the author of the comment and authenticated.'''
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)        
        if comment.author != request.user:
            return Response({"detail": "You do not have permission to delete this comment"},
                                status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({"detail": "Comment deleted successfully"}, status=status.HTTP_200_OK)


class CreateReply(APIView):
    '''***This API allows the creation of a new post.***<p>
    <b>Requirements</b>:
    - The user must be authenticated.
    - The user will need to use the token.<p>

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
    <b>2.2.</b> In the <b><i>comment_id integer path</i></b> provide a <b>comment_id</b> of the comment you want to reply to.<p>
    <b>2.3.</b> In the request body (application/json), add your reply to <b><i>{"body": "your reply comment here"}</i></b><p>
    <b>2.4.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>POST</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with the code itself. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
    '''
    serializer_class = ReplyCommentSerializer

    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)  # Retrieve the associated post
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReplyCommentSerializer(data=request.data)
        if serializer.is_valid():
            # Set the comment's author to the authenticated user
            serializer.save(author=request.user, parent_id=comment, post_id=comment.post_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModeratorRemoveComment(APIView):
    """Delete comment as moderator.

    - Need to provide a token from a user with moderator role;

    Press Try Out , insert comment id and then press execute.

    Moderator should be able to remove comments that are not according to the NaBB guidelines.
    """
    permission_classes = [IsAuthenticated, IsModeratorRole]
    serializer_class = ReplyCommentSerializer

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
            if request.user.role.is_moderator:
                comment.delete()
                return Response({"message": "Comment deleted successfully"})
            else:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
