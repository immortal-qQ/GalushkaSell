from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'category', 'price', 'header', 'description', 'status', 'image']


class TgUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'emoji_id', 'parent', 'created_on']


class FavouriteRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteRecord
        fields = '__all__'
