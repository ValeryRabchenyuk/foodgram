from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'get_user_subscription',
        'get_user_recipes')

    list_filter = ('username', 'email')
    search_fields = ('username', 'email')

    @admin.display(description='Сколько подписчиков')
    def get_user_subscription(self, object):
        return object.subscription.count()

    @admin.display(description='Сколько рецептов')
    def get_user_recipes(self, object):
        return object.recipe.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'subscriber',
        'author')

    search_fields = ('subscriber__username', 'author__username')
    list_editable = ('subscriber', 'author')
    list_filter = ('subscriber', 'author')
