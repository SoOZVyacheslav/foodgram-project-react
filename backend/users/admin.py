from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email', 'first_name', 'last_name',)
    list_display = ('username', 'email', 'first_name', 'last_name',)
    search_fields = ('first_name', 'last_name', 'username', 'email',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
