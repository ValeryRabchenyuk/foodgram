import re
# from rest_framework.serializers import ModelSerializer, SerializerMethodField

from django.contrib.auth.tokens import default_token_generator

from rest_framework import serializers

from djoser.serializers import UserCreateSerializer #UserSerializer

# from .constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from ..users.models import User, Subscription
from ..recipes.models import Tag


class SignUpSerializer(UserCreateSerializer):
    """Создание пользователя."""
# нужна проверка на символы
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
            return Subscription.objects.filter(
                subscriber=request.user,
                author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
