import re
# from rest_framework.serializers import ModelSerializer, SerializerMethodField

from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers

from djoser.serializers import UserCreateSerializer, UserSerializer

from .constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from .models import User, Subscription



class SignUpSerializer(UserCreateSerializer):
    """Создание пользователя."""

    class Mets:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )


class UserSerializer(serializers.ModelSerializer):
    """Существующий пользователь."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(subscriber=request.user, author=obj).exists()
        return False





class CustomUserSerializer(serializers.ModelSerializer):

    

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        read_only_fields = ('is_subscribed',)
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.subscriptions.filter(author=obj).exists()


class CustomCreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user