from rest_framework import serializers
from ..models.post import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']


class CategoriesSerializer(serializers.ModelSerializer):
    num_posts = serializers.SerializerMethodField()
    num_published_posts = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'category_name', 'num_posts', 'num_published_posts']

    def get_num_posts(self, obj):
        return obj.posts.count()

    def get_num_published_posts(self, obj):
        return obj.posts.filter(status='published').count()


class CategoryFilterSerializer(serializers.Serializer):
    category_id = serializers.CharField(max_length=255)