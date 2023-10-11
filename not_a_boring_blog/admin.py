from django.contrib import admin
from .models.comment import Comment
from .models.post import Post, Category
from .models.user import Role
from .models.views import View
from .models.repost_request import RepostRequest


class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_blogger', 'is_moderator', 'is_admin')
    list_filter = ('is_blogger', 'is_moderator', 'is_admin')


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user_id','get_categories', 'created_at', 'last_updated', 'status')
    list_filter = ('category__category_name', 'status')
    search_fields = ('title', 'body', 'description')

    def get_categories(self, obj):
        return ", ".join([category.category_name for category in obj.category.all()])
    get_categories.short_description = 'Category'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name')


class RepostRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester_id', 'post_id', 'status', 'created_at')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_id_id', 'author', 'created_at', 'parent_id')


admin.site.register(View)
admin.site.register(Comment, CommentAdmin)
admin.site.register(RepostRequest, RepostRequestAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Post, PostAdmin)
