from django.contrib import admin

from .models import (Tag,
                     Ingredient,
                     Recipe,
                     RecipeIngredient,
                     Favorite,
                     ShoppingList)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = ('name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)

    @admin.display(description='Число добавлений рецепта в избранное.')
    def added_to_favorite(self, obj):
        return obj.favorite.count()


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
