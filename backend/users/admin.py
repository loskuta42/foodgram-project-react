from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser, Subscribe


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'username')
    search_fields = ('username',)
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_filter = ('user',)
    search_fields = ('user',)
    empty_value_display = '-пусто-'
