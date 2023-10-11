from ..models.user import User
from ..models.post import Post
from ..models.views import View
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from datetime import datetime, timedelta, timezone
from not_a_boring_blog.serializers.view import ViewCountSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_post_view(request, post_id):
    """Creates an entry in view table when the user goes to post detail"""
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    cooldown_period = timedelta(minutes=int(post.min_read))
    if post.user_id == user:
        return Response({"message": "Author's own view is not counted"}, status=403)
    last_view = View.objects.filter(post_id=post.id, user_id=user.id).order_by('-timestamp').first()
    if not last_view or (datetime.now(timezone.utc) - last_view.timestamp) > cooldown_period:
        user = get_object_or_404(User, id=user.id)
        View.objects.create(post_id=post, user_id=user)
        return Response({"message": "View recorded successfully"}, status = status.HTTP_200_OK)
    return Response({"error": "Cooldown period not elapsed"}, status=429)



@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_post_views(request, post_id):
    """Counts Post view"""
    post = get_object_or_404(Post, pk=post_id)

    views = View.objects.filter(post_id=post_id)
    view_count = views.count()  # Calculate the view count based on the queryset
    serializer = ViewCountSerializer({'view_count': view_count})

    if view_count == 0:
        return Response({"detail": "No views found for this post"}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.data, status=status.HTTP_200_OK)
