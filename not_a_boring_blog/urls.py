from django.urls import path, include
from .views.view import create_post_view, get_post_views
from .views.post import (
    PostList, 
    PostDetail, 
    PostCreate, 
    GetPublicPosts, 
    GetUserPublicPosts,
    GetUserPosts,
    HidePost
    )
from .views.user import (
    UserList,
    RegisterUser,
    UpdateUser,
    LoginUser,
    LogoutUser,
    UpdateUserRole,
    ChangeUserPassword,
    UpdateUserBio,
)
from .views.comment import (
    PostCommentList,
    CreateComment,
    UpdateComment,
    CreateReply,
    ModeratorRemoveComment,
)
from .views.repost import (
    CreateRepostRequest,
    RepostRequestedReceivedList,
    RepostRequestsSentList,
    UpdateRepostRequestStatus,
    DeleteRepostRequestView,
)
from .views.category import (
    CreateCategory,
    ListCategories,
    PostsByCategory,
)


app_name = "not_a_boring_blog"
urlpatterns = [

    # categories
    path('category/create_category/', CreateCategory.as_view(), name='create_category'),
    path('category/list_categories/', ListCategories.as_view(), name='list_categories'),
    path('category/posts/<str:category_name>', PostsByCategory.as_view(), name='category_posts'),

    # post endpoints
    path('post/post_list/', PostList.as_view(), name='post-list'),
    path('post/post_detail/<int:pk>/', PostDetail.as_view(), name='post-detail'),
    path('post/post_create/', PostCreate.as_view(), name='post-create'),
    path('post/public_posts/', GetPublicPosts.as_view(), name='get-public-posts'),
    path('post/user_posts/<str:username>/', GetUserPublicPosts.as_view(), name='only-user-posts'),
    path('post/my_posts/', GetUserPosts.as_view(), name='my-posts'),
    path('post/hide_post/<int:pk>', HidePost.as_view(), name='hide-post'),

    #comments
    path('comment/comments/<int:post_id>/', PostCommentList.as_view(), name='comments'),
    path('comment/create_comment/<int:post_id>/', CreateComment.as_view(), name='create_comment'),
    path('comment/create_reply/<int:comment_id>/', CreateReply.as_view(), name='create_reply'),
    path('comment/update_comment/<int:comment_id>/', UpdateComment.as_view(), name='update_comment'),
    # ^ updates or deletes depending on the request method, works with comments as well as replies
    path('comment/moderator_rm_comment/<int:comment_id>/', ModeratorRemoveComment.as_view(), name='moderator_rm_comment'),

    # user endpoints
    path('user/change_password/', ChangeUserPassword.as_view(), name='change_password'),
    path('user/update_role/<str:username>/', UpdateUserRole.as_view(), name='update_role'),
    path('user/users_list/', UserList.as_view(), name='users_list'),
    path('user/register/', RegisterUser.as_view(), name='register'),
    path('user/update_user/', UpdateUser.as_view(), name='update_user'),
    path('user/update_bio/', UpdateUserBio.as_view(), name='update_bio'),
    path('user/login/', LoginUser.as_view(), name='login'),
    path('user/logout/', LogoutUser.as_view(), name='logout'),

    # repost request
    path('repost_request/request_repost/<int:post_id>/', CreateRepostRequest.as_view(), name='request_repost'),
    path('repost_request/requests_received/', RepostRequestedReceivedList.as_view(), name='requests_received'),
    path('repost_request/requests_sent/', RepostRequestsSentList.as_view(), name='requests_sent'),
    path('repost_request/update_request/<int:request_id>/', UpdateRepostRequestStatus.as_view(), name='request_update'),
    path('repost_request/delete_request/<int:request_id>/', DeleteRepostRequestView.as_view(), name='delete_repost_request'),

    # post views
    path('views/create_post_view/<int:post_id>/', create_post_view, name='create_post_view'),
    path('views/view_count/<int:post_id>/', get_post_views, name='post_views'),

]