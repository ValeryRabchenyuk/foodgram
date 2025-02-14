from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from .constants import (COOKING_MIN_TIME,
                        INGREDIENT_MAX_LENGTH,
                        INGREDIENT_MIN_AMOUNT,
                        MEASUREMENT_MAX_LENGTH,
                        RECIPE_NAME_MAX_LENGTH,
                        TAG_MAX_LENGTH,
                        SHORT_LINK_MAX_LENGTH)


User = get_user_model()


class Tag(models.Model):

    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Тег')

    slug = models.SlugField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Поле содержите недопустимый символ')])

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tag'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        max_length=INGREDIENT_MAX_LENGTH,
        verbose_name='Ингредиент')

    measurement_unit = models.CharField(
        max_length=MEASUREMENT_MAX_LENGTH,
        verbose_name='Единица измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты')

    tags = models.ManyToManyField(Tag, verbose_name='Теги')

    image = models.ImageField(
        upload_to='images',
        verbose_name='Картинка')

    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название блюда')

    text = models.TextField(verbose_name='Процесс приготовления')

    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(COOKING_MIN_TIME)])

    short_link = models.CharField(
        verbose_name='Короткая ссылка',
        max_length=SHORT_LINK_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True)

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Вспомогательная модель. Количество ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe')

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(INGREDIENT_MIN_AMOUNT)])

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Количество ингредиент'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient} — {self.amount}'


class FavoriteAndShoppingListModel(models.Model):
    """Абстрактная модель для избранных рецептов и списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь')

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} — {self.recipe}'


class Favorite(FavoriteAndShoppingListModel):
    """Избранные рецепты."""

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorite'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='favorite_unique')]

    def __str__(self):
        return f'{self.recipe} теперь в избранном.'


class ShoppingList(FavoriteAndShoppingListModel):
    """Список покупок."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        default_related_name = 'shopping_list'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='shoppinglist_unique')]

    def __str__(self):
        return f'Продукты для {self.recipe} добавлены в список покупок.'
