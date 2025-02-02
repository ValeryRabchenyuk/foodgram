from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.db.models import UniqueConstraint

from .constants import (TAG_MAX_LENGTH,
                        INGREDIENT_MAX_LENGTH,
                        MEASUREMENT_MAX_LENGTH,
                        RECIPE_NAME_MAX_LENGTH,
                        COOKING_MIN_TIME,
                        INGREDIENT_MIN_AMOUNT)


from users.models import User


class Tag(models.Model):

    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Название')

    slug = models.SlugField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Поле содержите недопустимый символ')])

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        max_length=INGREDIENT_MAX_LENGTH,
        verbose_name='Название')

    measurement_unit = models.CharField(
        max_length=MEASUREMENT_MAX_LENGTH,
        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):

    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингредиенты')

    tags = models.ManyToManyField('Tag', verbose_name='Теги')

    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка')

    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название блюда')

    text = models.TextField(verbose_name='Процесс приготовления')

    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(COOKING_MIN_TIME)])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Вспомогательная модель. Количество ингредиентов."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(INGREDIENT_MIN_AMOUNT)])

    class Meta:
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
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='favorite_unique')]

    def __str__(self):
        return f'{self.recipe.name} теперь в избранном.'


class ShoppingList(FavoriteAndShoppingListModel):
    """Список покупок."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingcart')]

    def __str__(self):
        return f'Продукты для {self.recipe.name} добавлены в список покупок.'
