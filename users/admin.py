from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    search_fields = ('username', 'email')
    ordering = ('username',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
