from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsOwnerOrReadOnly
from ..models.repost_request import RepostRequest, Post, User
from ..serializers.repost import (
    RepostSerializer,
    RepostRequestListSerializer,
    UpdateRepostRequestSerializer,
)
from django.shortcuts import get_object_or_404


class CreateRepostRequest(APIView):
    '''***This API allows the creation of a post request***<p>
    <b>Requirements</b>:
    - The user must be authenticated.
    - The user will need to use their token.<p>

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
    <b>2. PARAMETERS</b>:<p>
    <b>2.1.</b> In order to send a request for a repost, click on <b><i>Try it out</i></b> button.<p>
    <b>2.2.</b> In the <b><i>post_id integer path</i></b> provide a <b>post_id</b> of the existing post you want to repost.<p> 
    <strong>!!! DO NOT DO ANY MODIFICATIONS IN THE REQUEST BODY !!!</strong></p>
    <b>2.3.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>POST</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 201 message along with the code itself. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
    '''
    serializer_class = RepostSerializer

    def post(self, request, post_id):
        # Check if the user has already created a repost request for the same post
        post = get_object_or_404(Post, id=post_id)

        existing_request = RepostRequest.objects.filter(
            requester_id=request.user.id,
            post_id=post_id,
        ).first()

        if existing_request:
            return Response(
                {"detail": "You have already created a repost request for this post."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a serializer instance with the provided request data
        serializer_data = {
            #**request.data,
            'requester_id': request.user.id,
            'post_id': post_id,
        }
        serializer = RepostSerializer(data=serializer_data)

        if serializer.is_valid():
            # Create the repost request
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class RepostRequestedReceivedList(APIView):
    """***This API returns requests to post author***<p>
    <b>Requirements</b>:
    - The user must be authenticated.
    - The user will need to use their token.<p>

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
    <b>2. PARAMETERS</b>:<p>
    <b>2.1.</b> In order to get a list of your posts for a repost, click on <b><i>Try it out</i></b> button.<p>
    <b>2.2.</b>  Then press the <b><i>Execute</i></b> button in order to send a <b>GET</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with the list of posts with some info which were asked for a repost. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
    """

    def get(self, request):
        # Get the authenticated user (post owner)
        user = self.request.user
        # Filter repost requests for posts owned by the user
        queryset = RepostRequest.objects.filter(post_id__user_id=user.id)
        # Serialize the queryset
        serializer = RepostRequestListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RepostRequestsSentList(APIView):
    '''***This API returns requests sent by the user***<p>
    <b>Requirements</b>:
    - The user must be authenticated.
    - The user will need to use their token.<p>

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
    <b>2. PARAMETERS</b>:<p>
    <b>2.1.</b> In order to get a list of repost requests you've done, click on <b><i>Try it out</i></b> button.<p>
    <b>2.2.</b>  Then press the <b><i>Execute</i></b> button in order to send a <b>GET</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with the list of posts which you asked for a repost. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
    '''

    def get(self, request):
        user = self.request.user
        # Filter repost requests for requests owned by the user
        queryset = RepostRequest.objects.filter(requester_id=user.id)
        # Serialize the queryset
        serializer = RepostRequestListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateRepostRequestStatus(APIView):
    '''***Post author can update the status of a request by id - update status to accepted or denied***<p>
    <b>Requirements</b>:
    - The user must be authenticated.
    - The user will need to use their token.<p>

    ***HOW TO USE:***<p>
    <ul><b>1. AUTHENTICATION</b><p>
    <ul><b>1.1.</b>  Before making a request to this endpoint, ensure that you are authenticated, using your token. <p>
    ---> For this check <i><u>user/registration/</u></i> and <i><u>user/login/</u></i>.<p>    
    <b>1.2.</b> Apply the token, it should belong to the authenticated owner of the post.<p>
    !!! For this follow the steps:<p>
    ---> click on the image of a <b>lock</b> in the right corner of your highlighted box, <p> 
    ---> choose <b><i>tokenAuth</i></b>,<p> 
    ---> insert <b>Token</b> <b><i>YOUR_TOKEN_KEY</i></b> and <b>Authorize</b>.<p>
    ------------------------------------------------------------<p>
    <b>2. PARAMETERS</b>:<p>
    <b>2.1.</b> In order to send a request for a repost change status, click on <b><i>Try it out</i></b> button.<p>
    <b>2.2.</b> In the <b><i>request_id integer path</i></b> provide a <b>request_id</b> of the existing request.<p> 
    <b>2.3.</b> In the <b><i>Request body</i></b> change the default status <b>requested</b> to <b>approved</b> or <b>denied</b>.<p> 
    <b>2.4.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>PUT</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 200 message along with the code itself. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
    '''
    serializer_class = UpdateRepostRequestSerializer

    def put(self, request, request_id):
        # Get the authenticated user (post owner)
        user = self.request.user
        #breakpoint()

        try:
            # Retrieve the repost request by request id and check if it belongs to the user
            repost_request = RepostRequest.objects.get(id=request_id, post_id__user_id=user.id)
        except RepostRequest.DoesNotExist:
            return Response({"detail": "Repost request not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        # Create an instance of the update serializer with the repost request data
        serializer = UpdateRepostRequestSerializer(repost_request, data=request.data)

        if serializer.is_valid():
            # Update the status if it's a valid choice ("approved" or "denied")
            new_status = serializer.validated_data['status'].lower()
            if new_status in ['approved', 'denied']:
                repost_request.status = new_status
                repost_request.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid status choice"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteRepostRequestView(APIView):
    '''***This API requester can delete a request by its id***<p>
    <b>Requirements</b>:
    - The user must be authenticated.
    - The user will need to use their token.<p>

    ***HOW TO USE:***<p>
    <ul><b>1. AUTHENTICATION</b><p>
    <ul><b>1.1.</b>  Before making a request to this endpoint, ensure that you are authenticated, using your token. <p>
    ---> For this check <i><u>user/registration/</u></i> and <i><u>user/login/</u></i>.<p>    
    <b>1.2.</b> Apply the token, it should belong to the authenticated owner of the request.<p>
    !!! For this follow the steps:<p>
    ---> click on the image of a <b>lock</b> in the right corner of your highlighted box, <p> 
    ---> choose <b><i>tokenAuth</i></b>,<p> 
    ---> insert <b>Token</b> <b><i>YOUR_TOKEN_KEY</i></b> and <b>Authorize</b>.<p>
    ------------------------------------------------------------<p>
    <b>2. PARAMETERS</b>:<p>
    <b>2.1.</b> In order to delete your own repost request, click on <b><i>Try it out</i></b> button.<p>
    <b>2.2.</b> In the <b><i>request_id integer path</i></b> provide a <b>request_id</b> of the request you want to delete.<p> 
    <b>2.3.</b>  Press the <b><i>Execute</i></b> button in order to send a <b>DELETE</b> request to the API endpoint.<p>
    ---> If successful, the API will return a 204 message. <p>
    ---> If there are any errors, appropriate error messages will be returned.</ul></ul>
    '''
    def delete(self, request, request_id):
        # Get the authenticated user (post owner)
        user = self.request.user

        try:
            # Retrieve the repost request by request_id and check if it belongs to a post owned by the user
            repost_request = RepostRequest.objects.get(id=request_id, requester_id=user.id)
        except RepostRequest.DoesNotExist:
            return Response({"detail": "Repost request not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that repost_request is a valid RepostRequest instance
        if isinstance(repost_request, RepostRequest):
            # Delete the repost request
            repost_request.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Invalid repost request"}, status=status.HTTP_400_BAD_REQUEST)