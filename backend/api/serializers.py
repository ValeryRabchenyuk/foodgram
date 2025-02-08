import base64
import re

from django.core.files.base import ContentFile

from rest_framework import serializers

from djoser.serializers import UserCreateSerializer

from ..recipes.constants import COOKING_MIN_TIME
from ..recipes.models import (Favorite,
                              Ingredient,
                              Recipe,
                              RecipeIngredient,
                              ShoppingList,
                              Tag)

from ..users.models import Subscription, User


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class SignUpSerializer(UserCreateSerializer):
    """Создание пользователя."""

    password = serializers.CharField(write_only=True, required=True)

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

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=request.user,
                author=obj).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Создание связи рецепт-ингредиент."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Получение ингредиентов для рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')

    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    name = serializers.CharField(source='ingredient.name')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount', 'measurement_unit', 'name']


class RecipeReadSerializer(serializers.ModelSerializer):
    """Чтение рецепта."""

    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True,
        many=True,
        source='recipe_ingredients')
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
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        source='recipe_ingredients')
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

    def validate(self, attrs):
        tags = attrs.get('tags')
        ingredients = attrs.get('recipe_ingredients')
        if not tags:
            raise serializers.ValidationError(
                'Отсутствует обязательное поле tags.')

        if not ingredients:
            raise serializers.ValidationError(
                'Отсутствует обязательное поле ingredients.')

        ingredients_ids = [
            ingredient.get('ingredient').id for ingredient in ingredients]

        if len(set(ingredients_ids)) != len(ingredients):
            raise serializers.ValidationError(
                'Ингридиенты должны быть уникальными.')

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Теги должны быть уникальными.')

        return attrs

    def validate_cooking_time(self, value):
        if int(value) < 1:
            raise serializers.ValidationError('Нельзя приготовить так быстро.')
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужна фотография блюда.')
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
        self.create_recipeingredient(ingredients=ingredients, recipe=recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.recipe_ingredients.clear()
        self.create_recipeingredient(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Краткая информация о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time')
        read_only_fields = ('__all__',)


class FavoriteSerializer(serializers.ModelSerializer):
    """Избранные рецепты."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в Избранное.')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Список покупок."""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в Список покупок!')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class ReadSubscriptionSerializer(serializers.ModelSerializer):
    """Получение информации о подписках."""

    recipes = serializers.SerializerMethodField(method_name='get_recipe')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipe(self, author):
        recipes = author.recipes.all()
        request = self.context.get('request')
        if 'recipes_limit' in self.context.get('request').GET:
            recipes_limit = self.context.get('request').GET['recipes_limit']
            if recipes_limit.isdigit():
                recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}).data

    def get_recipes_count(self, user):
        return user.recipes.count()

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.following.filter(following=user).exists())


class SubscriptionSerializer(serializers.ModelSerializer):
    """Создание подписки."""

    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, attrs):
        subscriber = attrs['subscriber']
        author = attrs['author']

        if subscriber == author:
            raise serializers.ValidationError('Нельзя подписаться на себя.')

        is_subscription_exists = Subscription.objects.filter(
            subscriber=subscriber, author=author).exists()
        if is_subscription_exists:
            raise serializers.ValidationError('Вы уже подписаны.')
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscriptionSerializer(
            instance.author, context={'request': request}).data
