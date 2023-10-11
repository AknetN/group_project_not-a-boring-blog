from rest_framework import permissions

# to handle ownership-based permissions. 
# This class should check if the user making the request is the owner of the post.
class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):     
        if request.method in permissions.SAFE_METHODS:
            if obj.user_id == request.user or obj.status == 'published':
                return True
        return False


class IsAdminRole(permissions.BasePermission):
    SAFE_METHODS = ['GET', 'PUT', 'OPTIONS']
    def has_permission(self, request, view):
        if request.method in self.SAFE_METHODS:
            if request.user.role.is_admin:
                return True
        return False


class IsModeratorRole(permissions.BasePermission):
    SAFE_METHODS = ['GET', 'PUT', 'OPTIONS', 'DELETE']

    def has_permission(self, request, view):
        if request.method in self.SAFE_METHODS:
            if request.user.role.is_moderator:
                return True
        return False


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Check if the request user is the author of the comment.
            if obj.author == request.user:
                return True
        return False
