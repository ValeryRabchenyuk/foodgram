import re
import base64
# from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.core.files.base import ContentFile
from django.contrib.auth.tokens import default_token_generator

from rest_framework import serializers, status

from djoser.serializers import UserCreateSerializer


from ..users.models import User, Subscription
from ..recipes.models import (Tag,
                              Ingredient,
                              Recipe,
                              RecipeIngredient,
                              ShoppingList,
                              Favorite)

from ..recipes.constants import COOKING_MIN_TIME


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
            'password')

    def validate_username(self, data):
        pattern = re.compile(r'^[\w.@+-]+\Z')
        if not pattern.match(data):
            raise serializers.ValidationError('Недопустимый символ')
        return data


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
            'is_subscribed')

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


class IngredientSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер короткого представления ингредиента для рецепта"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Чтение рецепта."""

    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe')
    is_favorited = serializers.BooleanField(read_only=True)                                     # ПРОВЕРИТЬ
    is_in_shopping_cart = serializers.BooleanField(read_only=True)                              # ПРОВЕРИТЬ

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Создание и изменение рецепта."""

    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe')
    cooking_time = serializers.IntegerField(min_value=COOKING_MIN_TIME)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time')

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужны ингредиенты.', status.HTTP_400_BAD_REQUEST)
        ingredients = set()
        for ingredient in value:
            if ingredient not in self.instance.recipes.all():
                raise serializers.ValidationError(
                    'Такого ингридента нет.',
                    status.HTTP_400_BAD_REQUEST)
            obj = Ingredient.objects.get(id=ingredient['id'])
            if obj in ingredients:
                raise serializers.ValidationError(
                    'Такой ингридент уже есть.',
                    status.HTTP_400_BAD_REQUEST)
            ingredients.add(obj)
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нет тегов.',
                status.HTTP_400_BAD_REQUEST)
        tags = set()
        for tag in value:
            if tag in tags:
                raise serializers.ValidationError(
                    'Такой тег уже есть.',
                    status.HTTP_400_BAD_REQUEST)
            tags.add(tag)
        return value

    def validate_cooking_time(self, value):
        if int(value) < 1:
            raise serializers.ValidationError('Нельзя приготовить так быстро.')
        return value

    def validate_image(self, value):
        if not value: 
            raise serializers.ValidationError(
                'Нужна фотография блюда.',
                status.HTTP_400_BAD_REQUEST)
        return value

    def create_recipeingredient(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredients=Ingredient.objects.get(id=ingredient['id']),
                recipes=recipe,
                amount=ingredient['amount']) for ingredient in ingredients])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipeingredient(ingredients=ingredients, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_recipeingredient(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance=instance).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткое отображение рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time')
        read_only_fields = ("__all__",)


class FavoriteSerializer(serializers.ModelSerializer):
    """Избранные рецепты."""

    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в Избранное.')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe,
                                     context=self.context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Список покупок."""

    class Meta:
        model = ShoppingList
        fields = '__all__'

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe,
                                     context=self.context).data

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в Список покупок!')
        return data
