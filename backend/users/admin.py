from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


@admin.register(User)
class UsersAdmin(UserAdmin):

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name')

    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'subscriber',
        'author')

    search_fields = ('subscriber__username', 'author__username')
    list_editable = ('subscriber', 'author')
    list_filter = ('subscriber', 'author')
