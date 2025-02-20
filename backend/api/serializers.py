import re

from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from api.helpers import Base64ImageField
from recipes.constants import COOKING_MIN_TIME
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingList,
                            Tag)
from users.constants import USERNAME_MAX_LENGTH
from users.models import Subscription, User


class SignUpSerializer(UserCreateSerializer):
    """Создание пользователя."""

    password = serializers.CharField(write_only=True, required=True)

    first_name = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH)

    last_name = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH)

    class Meta:
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

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return user.is_authenticated and user.subscriber.filter(
            author=author).exists()


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

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
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_in_favorite')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_list')

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

    def get_is_in_favorite(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favorite.filter(recipe=obj).exists())

    def get_is_in_shopping_list(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.shopping_list.filter(recipe=obj).exists())


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
        if int(value) < COOKING_MIN_TIME:
            raise serializers.ValidationError('Нельзя приготовить так быстро.')
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужна фотография блюда.')
        return value

    def tags_and_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(recipe=recipe, **ingredient)
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        validated_data.pop('author', None)
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.tags_and_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self.tags_and_ingredients(instance, tags, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Краткая информация о рецепте."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class BaseFavoriteShoppingSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для избранного и списка покупок."""

    class Meta:
        abstract = True

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        model_name = self.Meta.model.__name__.lower()

        if model_name == 'favorite':
            if user.favorite.filter(recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Рецепт уже добавлен в Избранное.')
        if model_name == 'shoppinglist':
            if user.shopping_list.filter(recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Рецепт уже добавлен в Список покупок!')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class FavoriteSerializer(BaseFavoriteShoppingSerializer):
    """Избранные рецепты."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingListSerializer(BaseFavoriteShoppingSerializer):
    """Список покупок."""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')


class ReadSubscriptionSerializer(serializers.ModelSerializer):
    """Получение информации о подписках."""

    recipes = serializers.SerializerMethodField(method_name='get_recipe')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')
    is_subscribed = serializers.BooleanField(default=True)

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
                and request.user.subscriber.filter(author=user).exists())


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
        return ReadSubscriptionSerializer(
            instance.author, context={'request': request}).data
