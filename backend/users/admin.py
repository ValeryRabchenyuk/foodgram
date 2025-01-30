from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):

    list_display = ('id', 'username', 'email', 'first_name', 'last_name',)
    search_fields = ('username', 'email')


admin.site.register(Subscription)


    # list_editable = ('is_staff',)
    # list_filter = ('username',)
    # list_display_links = ('id', 'username', 'email', 'full_name')

# @admin.register(Follow)
# class FollowAdmin(admin.ModelAdmin):
#     list_display = (
#         'following',
#         'follower',
#     )
#     search_fields = ('follower',)